# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-21-scan-persistence/spec.md

## Technical Requirements

### SQLite Database

Single file at `/data/aston-osint.db`, mounted as Docker volume.

### Schema

```sql
CREATE TABLE IF NOT EXISTS scans (
    id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    kwargs TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    raw_results TEXT,
    filtered_results TEXT,
    disambiguation TEXT,
    sources_hit TEXT NOT NULL DEFAULT '[]',
    sources_failed TEXT NOT NULL DEFAULT '[]',
    duration_ms INTEGER DEFAULT 0,
    error TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);
```

Status values: `pending`, `running`, `complete`, `failed`

### Database Module (app/db.py)

```python
def init_db(): ...
def create_scan(scan_id, query, kwargs) -> str: ...
def update_scan_running(scan_id): ...
def update_scan_complete(scan_id, raw_results, filtered_results, disambiguation, sources_hit, sources_failed, duration_ms): ...
def update_scan_failed(scan_id, error): ...
def update_filtered_results(scan_id, filtered_results, disambiguation): ...
def get_scan(scan_id) -> dict | None: ...
def list_scans(limit=50, offset=0) -> dict: ...
```

JSON serialization: results are stored as JSON strings using `dataclasses.asdict()`.

### Async Scan Flow

```
POST /api/v1/scan
  1. Generate scan_id (UUID)
  2. Insert row with status='pending'
  3. Launch background task via asyncio.create_task()
  4. Return { scan_id, status: 'pending' } immediately

Background task:
  1. Update status='running'
  2. Fan out to 5 sources (asyncio.gather)
  3. Name filter (Pass 1)
  4. Claude entity resolution (Pass 2)
  5. Extract facets
  6. Update status='complete' with all results
  7. On exception: update status='failed' with error

GET /api/v1/scans/{id}
  - If status='pending' or 'running': return { scan_id, status, query }
  - If status='complete': return full results + disambiguation
  - If status='failed': return { scan_id, status, error }
```

### UI Polling

```javascript
async function pollScan(scanId) {
  const interval = setInterval(async () => {
    const resp = await fetch('/api/v1/scans/' + scanId);
    const data = await resp.json();

    if (data.status === 'complete') {
      clearInterval(interval);
      // show wizard or results
    } else if (data.status === 'failed') {
      clearInterval(interval);
      // show error
    }
    // else keep polling
  }, 2000);
}
```

### Refine Endpoint Update

POST /api/v1/scan/{id}/refine:
1. Read raw_results from database (not memory)
2. Apply filters + dismiss
3. Re-run Claude entity resolution
4. Update filtered_results in database
5. Return updated results

### Docker Volume

```bash
# deploy.sh
docker run ... -v aston-osint-data:/data ...
```

### History UI (history.html)

**List view:**
- Cards showing: query name, status badge, date, match count, duration
- Running scans show spinner
- Click navigates to detail

**Detail view:**
- Same page with `?id={scan_id}` query param
- Shows query params, filtered results (card format), toggle for raw results

### File Changes

```
app/
├── db.py              # NEW: SQLite module
├── scan_store.py      # REMOVE
├── orchestrator.py    # UPDATE: async background task
├── main.py            # UPDATE: return immediately, add polling
static/
├── history.html       # NEW: history page
├── index.html         # UPDATE: poll instead of await
```

## External Dependencies

None — SQLite is in Python's standard library.
