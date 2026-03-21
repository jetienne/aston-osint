# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-21-scan-persistence/spec.md

## Technical Requirements

### SQLite Database

Single file at `/data/aston-osint.db` inside the container, mounted as a Docker volume for persistence.

### Schema

```sql
CREATE TABLE IF NOT EXISTS scans (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    kwargs TEXT NOT NULL DEFAULT '{}',
    raw_results TEXT NOT NULL DEFAULT '[]',
    filtered_results TEXT NOT NULL DEFAULT '[]',
    sources_hit TEXT NOT NULL DEFAULT '[]',
    sources_failed TEXT NOT NULL DEFAULT '[]',
    duration_ms INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

- `id`: UUID (same as current scan_id)
- `query`: the search name
- `kwargs`: JSON of nationality, birth_year, company
- `raw_results`: JSON of results after name filtering (before Claude)
- `filtered_results`: JSON of results after entity resolution
- `sources_hit`: JSON array of source names that returned data
- `sources_failed`: JSON array of source names that errored
- `duration_ms`: total scan duration
- `created_at`: ISO 8601 timestamp

### Database Module

```python
# app/db.py
import json
import sqlite3
import uuid

DB_PATH = '/data/aston-osint.db'

def init_db():
    """Create tables if they don't exist."""

def save_scan(scan_id, query, kwargs, raw_results, filtered_results, sources_hit, sources_failed, duration_ms):
    """Insert a scan record."""

def get_scan(scan_id):
    """Get a single scan by ID. Returns dict or None."""

def list_scans(limit=50, offset=0):
    """List scans ordered by created_at desc. Returns list of dicts (without full results)."""

def update_filtered_results(scan_id, filtered_results):
    """Update filtered results after refine."""
```

Results are serialized to JSON using a custom encoder that handles dataclasses.

### Docker Volume

```yaml
# In deploy.sh docker run command:
-v aston-osint-data:/data
```

### API Endpoints

#### GET /api/v1/scans

List all scans, most recent first. Returns summary without full results.

```json
{
  "scans": [
    {
      "id": "uuid",
      "query": "Vladimir Putin",
      "kwargs": {"nationality": "Russia"},
      "sources_hit": ["aleph", "opensanctions"],
      "sources_failed": ["gdelt"],
      "match_count": 4,
      "duration_ms": 5200,
      "created_at": "2026-03-21T15:30:00"
    }
  ],
  "total": 42
}
```

#### GET /api/v1/scans/{scan_id}

Full scan detail including raw and filtered results.

```json
{
  "id": "uuid",
  "query": "Vladimir Putin",
  "kwargs": {"nationality": "Russia"},
  "raw_results": [...],
  "filtered_results": [...],
  "sources_hit": [...],
  "sources_failed": [...],
  "duration_ms": 5200,
  "created_at": "2026-03-21T15:30:00"
}
```

### Orchestrator Changes

1. After scan completes, save to database (replaces `scan_store.save_scan`)
2. Return `scan_id` as before
3. Refine endpoint reads from database instead of in-memory store

### UI: History Page

New sidebar link "History" → `/history.html`

**List view:**
- Table/cards showing: query name, date, match count, sources hit
- Click to view details

**Detail view:**
- Show on the same page or navigate to `/history.html?id={scan_id}`
- Display query parameters, filtered results (same card format as scan page), and a toggle to show raw results

### File Structure

```
app/
├── db.py              # SQLite module (replaces scan_store.py)
├── ...
static/
├── history.html       # Scan history page
├── ...
```

## External Dependencies

- None — SQLite is built into Python's standard library
