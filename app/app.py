#!/usr/bin/env python3
"""
Flask backend for dynamic recruiting dashboard
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'recruiting.db')

def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    """Convert sqlite row to dictionary"""
    return {key: row[key] for key in row.keys()}

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    conn = get_db()
    cursor = conn.cursor()

    stats = {}

    # Total counts
    cursor.execute("SELECT COUNT(*) FROM candidates")
    stats['total_candidates'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiences")
    stats['total_experiences'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT company) FROM experiences")
    stats['unique_companies'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT location) FROM candidates WHERE location IS NOT NULL")
    stats['unique_locations'] = cursor.fetchone()[0]

    # Recent additions (last 30 days)
    cursor.execute("""
        SELECT COUNT(*) FROM candidates
        WHERE added_to_sequence_at >= date('now', '-30 days')
    """)
    stats['recent_additions'] = cursor.fetchone()[0]

    # Top companies
    cursor.execute("""
        SELECT company, COUNT(*) as count
        FROM experiences
        GROUP BY company
        ORDER BY count DESC
        LIMIT 10
    """)
    stats['top_companies'] = [dict(row) for row in cursor.fetchall()]

    # Top locations
    cursor.execute("""
        SELECT location, COUNT(*) as count
        FROM candidates
        WHERE location IS NOT NULL
        GROUP BY location
        ORDER BY count DESC
        LIMIT 10
    """)
    stats['top_locations'] = [dict(row) for row in cursor.fetchall()]

    # Role distribution
    cursor.execute("""
        SELECT
            CASE
                WHEN title LIKE '%Engineer%' OR title LIKE '%Developer%' THEN 'Engineering'
                WHEN title LIKE '%Manager%' OR title LIKE '%Director%' THEN 'Management'
                WHEN title LIKE '%Analyst%' THEN 'Analytics'
                WHEN title LIKE '%Security%' THEN 'Security'
                WHEN title LIKE '%Data%' THEN 'Data'
                ELSE 'Other'
            END as role_category,
            COUNT(*) as count
        FROM experiences
        WHERE sequence = 0
        GROUP BY role_category
        ORDER BY count DESC
    """)
    stats['role_distribution'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify(stats)

@app.route('/api/candidates')
def get_candidates():
    """Get candidates with filtering, sorting, and pagination"""
    conn = get_db()
    cursor = conn.cursor()

    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    company = request.args.get('company', '')
    title = request.args.get('title', '')
    role_category = request.args.get('role_category', '')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    # Build WHERE clause
    where_conditions = []
    params = []

    if search:
        where_conditions.append("""
            (c.full_name LIKE ? OR
             c.location LIKE ? OR
             EXISTS (SELECT 1 FROM experiences e WHERE e.candidate_id = c.id AND
                     (e.title LIKE ? OR e.company LIKE ?)))
        """)
        search_pattern = f'%{search}%'
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    if location:
        where_conditions.append("c.location LIKE ?")
        params.append(f'%{location}%')

    if company:
        where_conditions.append("""
            EXISTS (SELECT 1 FROM experiences e WHERE e.candidate_id = c.id AND e.company LIKE ?)
        """)
        params.append(f'%{company}%')

    if title:
        where_conditions.append("""
            EXISTS (SELECT 1 FROM experiences e WHERE e.candidate_id = c.id AND e.title LIKE ?)
        "")
        params.append(f'%{title}%')

    if role_category:
        category_filter = {
            'engineering': '%Engineer%',
            'management': '%Manager%',
            'analytics': '%Analyst%',
            'security': '%Security%',
            'data': '%Data%'
        }.get(role_category.lower(), '%')
        where_conditions.append("""
            EXISTS (SELECT 1 FROM experiences e WHERE e.candidate_id = c.id AND e.title LIKE ?)
        """)
        params.append(category_filter)

    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

    # Validate sort column
    valid_sort_columns = ['id', 'full_name', 'location', 'first_outreach_at', 'added_to_sequence_at']
    if sort_by not in valid_sort_columns:
        sort_by = 'id'

    sort_direction = 'DESC' if sort_order.lower() == 'desc' else 'ASC'

    # Get total count
    count_query = f"SELECT COUNT(*) FROM candidates c {where_clause}"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]

    # Get candidates
    query = f"""
        SELECT c.*,
               (SELECT COUNT(*) FROM experiences WHERE candidate_id = c.id) as experience_count
        FROM candidates c
        {where_clause}
        ORDER BY c.{sort_by} {sort_direction}
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, params + [per_page, (page - 1) * per_page])
    candidates = [dict(row) for row in cursor.fetchall()]

    # Get experiences for each candidate
    for candidate in candidates:
        cursor.execute("""
            SELECT * FROM experiences
            WHERE candidate_id = ?
            ORDER BY sequence ASC
        """, (candidate['id'],))
        candidate['experiences'] = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        'candidates': candidates,
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_count + per_page - 1) // per_page
    })

@app.route('/api/candidates/<int:candidate_id>')
def get_candidate(candidate_id):
    """Get single candidate with all details"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({'error': 'Candidate not found'}), 404

    candidate = dict(row)

    cursor.execute("""
        SELECT * FROM experiences
        WHERE candidate_id = ?
        ORDER BY sequence ASC
    """, (candidate_id,))
    candidate['experiences'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify(candidate)

@app.route('/api/filters')
def get_filters():
    """Get available filter options"""
    conn = get_db()
    cursor = conn.cursor()

    filters = {}

    # Locations (cities)
    cursor.execute("""
        SELECT DISTINCT location_city as value, location_city as label
        FROM candidates
        WHERE location_city IS NOT NULL AND location_city != ''
        ORDER BY location_city
    """)
    filters['locations'] = [dict(row) for row in cursor.fetchall()]

    # States
    cursor.execute("""
        SELECT DISTINCT location_state as value, location_state as label
        FROM candidates
        WHERE location_state IS NOT NULL AND location_state != ''
        ORDER BY location_state
    """)
    filters['states'] = [dict(row) for row in cursor.fetchall()]

    # Companies
    cursor.execute("""
        SELECT DISTINCT company as value, company as label
        FROM experiences
        WHERE company IS NOT NULL AND company != ''
        ORDER BY company
    """)
    filters['companies'] = [dict(row) for row in cursor.fetchall()]

    # Job titles (unique)
    cursor.execute("""
        SELECT DISTINCT title as value, title as label
        FROM experiences
        WHERE title IS NOT NULL AND title != ''
        ORDER BY title
        LIMIT 100
    """)
    filters['titles'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify(filters)

@app.route('/api/search/advanced', methods=['POST'])
def advanced_search():
    """Advanced SQL search with custom queries"""
    conn = get_db()
    cursor = conn.cursor()

    data = request.get_json()
    query_type = data.get('query_type', 'simple')

    if query_type == 'company_hoppers':
        # Find candidates who have worked at multiple companies
        cursor.execute("""
            SELECT c.*, COUNT(e.id) as company_count
            FROM candidates c
            JOIN experiences e ON c.id = e.candidate_id
            GROUP BY c.id
            HAVING company_count >= 3
            ORDER BY company_count DESC
            LIMIT 50
        """)
        results = [dict(row) for row in cursor.fetchall()]

    elif query_type == 'senior_candidates':
        # Find candidates with senior-level titles
        cursor.execute("""
            SELECT DISTINCT c.*, e.title, e.company
            FROM candidates c
            JOIN experiences e ON c.id = e.candidate_id
            WHERE e.title LIKE '%Senior%' OR e.title LIKE '%Lead%' OR e.title LIKE '%Principal%'
            ORDER BY c.full_name
            LIMIT 50
        """)
        results = [dict(row) for row in cursor.fetchall()]

    elif query_type == 'recent_joins':
        # Find candidates added recently
        cursor.execute("""
            SELECT * FROM candidates
            WHERE added_to_sequence_at >= date('now', '-90 days')
            ORDER BY added_to_sequence_at DESC
            LIMIT 50
        """)
        results = [dict(row) for row in cursor.fetchall()]

    elif query_type == 'by_company':
        # Find all candidates who worked at a specific company
        company = data.get('company', '')
        cursor.execute("""
            SELECT DISTINCT c.*, e.title, e.company
            FROM candidates c
            JOIN experiences e ON c.id = e.candidate_id
            WHERE e.company LIKE ?
            ORDER BY c.full_name
        """, (f'%{company}%',))
        results = [dict(row) for row in cursor.fetchall()]

    elif query_type == 'by_location':
        # Find candidates by location
        location = data.get('location', '')
        cursor.execute("""
            SELECT * FROM candidates
            WHERE location LIKE ?
            ORDER BY full_name
        """, (f'%{location}%',))
        results = [dict(row) for row in cursor.fetchall()]

    else:
        return jsonify({'error': 'Unknown query type'}), 400

    conn.close()
    return jsonify({'results': results, 'count': len(results)})

@app.route('/api/query', methods=['POST'])
def custom_query():
    """Execute custom SQL query (read-only)"""
    conn = get_db()
    cursor = conn.cursor()

    data = request.get_json()
    sql = data.get('query', '').strip()

    # Only allow SELECT queries
    if not sql.upper().startswith('SELECT'):
        return jsonify({'error': 'Only SELECT queries are allowed'}), 403

    # Block dangerous keywords
    dangerous = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'EXEC', 'EXECUTE']
    if any(keyword in sql.upper() for keyword in dangerous):
        return jsonify({'error': 'Query contains forbidden keywords'}), 403

    try:
        cursor.execute(sql)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({col: val for col, val in zip(columns, row)})

        conn.close()
        return jsonify({
            'columns': columns,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/export')
def export_candidates():
    """Export candidates to CSV"""
    import csv
    import io

    conn = get_db()
    cursor = conn.cursor()

    search = request.args.get('search', '')
    location = request.args.get('location', '')

    query = """
        SELECT c.*, e.title as current_title, e.company as current_company
        FROM candidates c
        LEFT JOIN experiences e ON c.id = e.candidate_id AND e.sequence = 0
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND c.full_name LIKE ?"
        params.append(f'%{search}%')

    if location:
        query += " AND c.location LIKE ?"
        params.append(f'%{location}%')

    cursor.execute(query, params)
    rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Name', 'Location', 'Current Title', 'Current Company', 'LinkedIn'])

    # Write data
    for row in rows:
        writer.writerow([
            row['full_name'],
            row['location'],
            row['current_title'] or '',
            row['current_company'] or '',
            row['linkedin_url'] or ''
        ])

    conn.close()

    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=candidates.csv'
    }

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Caymus Recruiting API...")
    print("📊 Database:", DB_PATH)
    print("\nAPI Endpoints:")
    print("  GET  /api/stats          - Dashboard statistics")
    print("  GET  /api/candidates       - List candidates (with filters)")
    print("  GET  /api/candidates/<id> - Get single candidate")
    print("  GET  /api/filters         - Get filter options")
    print("  POST /api/search/advanced - Advanced search")
    print("  POST /api/query           - Custom SQL query")
    print("  GET  /api/export         - Export to CSV")
    print("\n🌐 Server running at http://localhost:5000")
    print("\nPress CTRL+C to stop")
    app.run(debug=True, host='0.0.0.0', port=5000)
