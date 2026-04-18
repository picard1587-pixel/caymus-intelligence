# Caymus Dynamic Recruiting Dashboard

A dynamic recruiting dashboard with SQLite database backend, SQL querying capabilities, and real-time filtering.

## Features

### 🗄️ **SQLite Database Backend**
- CSV data imported into structured SQLite database
- Fast queries with indexed columns
- Relational data model (candidates + experiences)

### 🔍 **Advanced Filtering**
- Filter by location, company, title
- Full-text search across all fields
- Real-time results with pagination

### ⚡ **SQL Query Editor**
- Built-in SQL editor with syntax highlighting
- Pre-built quick queries
- Custom SQL execution (SELECT only)
- Export results to CSV

### 📊 **Dashboard Analytics**
- Real-time statistics
- Top companies and locations
- Role distribution charts
- Recent activity tracking

### 🔎 **Advanced Search**
- Company hoppers (3+ companies)
- Senior candidates (Senior/Lead/Principal)
- Recent joins (last 90 days)
- Custom search by company or location

## Quick Start

### Option 1: Run with Batch File (Windows)
```batch
# Navigate to the app folder
cd "C:\Users\Picard\Projects\Caymus AI\app"

# Run the start script
start.bat
```

### Option 2: Manual Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Import CSV data (first run only):**
```bash
python import_csv.py
```

3. **Start the server:**
```bash
python app.py
```

4. **Open your browser:**
Navigate to `http://localhost:5000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/candidates` | List candidates (with filters) |
| GET | `/api/candidates/<id>` | Get single candidate |
| GET | `/api/filters` | Get filter options |
| POST | `/api/search/advanced` | Advanced search |
| POST | `/api/query` | Execute custom SQL |
| GET | `/api/export` | Export to CSV |

## Database Schema

### candidates table
- id, full_name, first_name, last_name
- linkedin_url, location, location_city, location_state, location_country
- first_outreach_at, added_to_sequence_at

### experiences table
- id, candidate_id, title, company, website, linkedin
- start_date, end_date, is_current, sequence

## Example SQL Queries

```sql
-- Find all candidates with "Engineer" in their title
SELECT c.full_name, e.title, e.company
FROM candidates c
JOIN experiences e ON c.id = e.candidate_id
WHERE e.title LIKE '%Engineer%'

-- Top 10 companies by candidate count
SELECT company, COUNT(*) as count
FROM experiences
GROUP BY company
ORDER BY count DESC
LIMIT 10

-- Candidates in Kansas City area
SELECT * FROM candidates
WHERE location LIKE '%Kansas%'

-- Current roles for all candidates
SELECT c.full_name, e.title, e.company
FROM candidates c
JOIN experiences e ON c.id = e.candidate_id
WHERE e.is_current = 1
```

## File Structure

```
app/
├── import_csv.py          # CSV to SQLite importer
├── app.py                 # Flask backend API
├── index.html             # Frontend application
├── requirements.txt       # Python dependencies
├── start.bat             # Windows startup script
├── recruiting.db         # SQLite database (created on first run)
└── README.md
```

## Development

To modify the application:

1. **Backend changes:** Edit `app.py` and restart the server
2. **Frontend changes:** Edit `index.html` and refresh browser
3. **Database reset:** Delete `recruiting.db` and re-run `import_csv.py`
