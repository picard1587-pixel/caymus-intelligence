#!/usr/bin/env python3
"""
Import CSV data into SQLite database for dynamic querying
"""

import sqlite3
import csv
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'recruiting.db')
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'final_pin.csv')

def init_database():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS experiences")
    cursor.execute("DROP TABLE IF EXISTS candidates")

    # Create candidates table
    cursor.execute("""
        CREATE TABLE candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            linkedin_url TEXT,
            location TEXT,
            location_city TEXT,
            location_state TEXT,
            location_country TEXT,
            first_outreach_at TEXT,
            added_to_sequence_at TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create experiences table
    cursor.execute("""
        CREATE TABLE experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            website TEXT,
            linkedin TEXT,
            start_date TEXT,
            end_date TEXT,
            is_current BOOLEAN DEFAULT 0,
            sequence INTEGER DEFAULT 0,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        )
    """)

    # Create indexes for fast filtering
    cursor.execute("CREATE INDEX idx_candidates_location ON candidates(location)")
    cursor.execute("CREATE INDEX idx_candidates_name ON candidates(full_name)")
    cursor.execute("CREATE INDEX idx_experiences_company ON experiences(company)")
    cursor.execute("CREATE INDEX idx_experiences_title ON experiences(title)")
    cursor.execute("CREATE INDEX idx_experiences_candidate ON experiences(candidate_id)")

    conn.commit()
    conn.close()
    print("✓ Database initialized")

def parse_location(location_str):
    """Parse location into components"""
    if not location_str:
        return None, None, None

    parts = [p.strip() for p in location_str.split(',')]
    city = parts[0] if len(parts) > 0 else None
    state = parts[1] if len(parts) > 1 else None
    country = parts[-1] if len(parts) > 0 else None

    return city, state, country

def parse_date(date_str):
    """Parse date string to ISO format"""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        return dt.isoformat()
    except:
        return date_str

def import_csv():
    """Import CSV data into database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        candidates_count = 0
        experiences_count = 0

        for row in reader:
            # Parse candidate info
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            full_name = f"{first_name} {last_name}".strip() or row.get('candidate.name', '').strip()

            location = row.get('candidate.location', '').strip()
            city, state, country = parse_location(location)

            # Insert candidate
            cursor.execute("""
                INSERT INTO candidates
                (full_name, first_name, last_name, linkedin_url, location, location_city, location_state, location_country, first_outreach_at, added_to_sequence_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                full_name, first_name, last_name,
                row.get('candidate.linkedin', '').strip(),
                location, city, state, country,
                parse_date(row.get('candidateSequence.firstOutreachAt', '')),
                parse_date(row.get('candidateSequence.addedToSequenceAt', ''))
            ))

            candidate_id = cursor.lastrowid
            candidates_count += 1

            # Parse experiences (up to 4)
            for i in range(4):
                title_key = f'candidate.experiences.{i}.title'
                company_key = f'candidate.experiences.{i}.company'

                title = row.get(title_key, '').strip()
                company = row.get(company_key, '').strip()

                if title and company:
                    start_date = parse_date(row.get(f'candidate.experiences.{i}.startDate', ''))
                    end_date = parse_date(row.get(f'candidate.experiences.{i}.endDate', ''))
                    is_current = 1 if not end_date else 0

                    cursor.execute("""
                        INSERT INTO experiences
                        (candidate_id, title, company, website, linkedin, start_date, end_date, is_current, sequence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        candidate_id, title, company,
                        row.get(f'candidate.experiences.{i}.website', '').strip(),
                        row.get(f'candidate.experiences.{i}.linkedin', '').strip(),
                        start_date, end_date, is_current, i
                    ))
                    experiences_count += 1

    conn.commit()
    conn.close()

    print(f"✓ Imported {candidates_count} candidates")
    print(f"✓ Imported {experiences_count} experiences")

def get_stats():
    """Get database statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM candidates")
    candidates = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM experiences")
    experiences = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT company) FROM experiences")
    companies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT location) FROM candidates")
    locations = cursor.fetchone()[0]

    cursor.execute("""
        SELECT company, COUNT(*) as count
        FROM experiences
        GROUP BY company
        ORDER BY count DESC
        LIMIT 10
    """)
    top_companies = cursor.fetchall()

    cursor.execute("""
        SELECT location, COUNT(*) as count
        FROM candidates
        WHERE location IS NOT NULL
        GROUP BY location
        ORDER BY count DESC
        LIMIT 10
    """)
    top_locations = cursor.fetchall()

    conn.close()

    return {
        'candidates': candidates,
        'experiences': experiences,
        'companies': companies,
        'locations': locations,
        'top_companies': top_companies,
        'top_locations': top_locations
    }

if __name__ == '__main__':
    print("🔧 Initializing recruiting database...")
    init_database()
    import_csv()

    stats = get_stats()
    print("\n📊 Database Statistics:")
    print(f"   Candidates: {stats['candidates']}")
    print(f"   Experiences: {stats['experiences']}")
    print(f"   Unique Companies: {stats['companies']}")
    print(f"   Unique Locations: {stats['locations']}")
    print("\n🎯 Top Companies:")
    for company, count in stats['top_companies']:
        print(f"   {company}: {count}")
    print("\n📍 Top Locations:")
    for location, count in stats['top_locations']:
        print(f"   {location}: {count}")
