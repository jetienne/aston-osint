# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2026-03-21-scan-persistence/spec.md

## Endpoints

### GET /api/v1/scans

**Purpose:** List all scans, most recent first
**Parameters:**
- `limit` (query, optional, default 50): max results
- `offset` (query, optional, default 0): pagination offset

**Response:**
```json
{
  "scans": [
    {
      "id": "uuid",
      "query": "Vladimir Putin",
      "kwargs": {"nationality": "Russia"},
      "sources_hit": ["aleph", "opensanctions", "icij"],
      "sources_failed": ["gdelt"],
      "match_count": 4,
      "duration_ms": 5200,
      "created_at": "2026-03-21T15:30:00"
    }
  ],
  "total": 42
}
```

### GET /api/v1/scans/{scan_id}

**Purpose:** Get full scan detail with raw and filtered results
**Response:**
```json
{
  "id": "uuid",
  "query": "Vladimir Putin",
  "kwargs": {"nationality": "Russia"},
  "raw_results": [
    {
      "source": "opensanctions",
      "query": "Vladimir Putin",
      "matches": [...],
      "duration_ms": 320,
      "error": null
    }
  ],
  "filtered_results": [
    {
      "source": "opensanctions",
      "query": "Vladimir Putin",
      "matches": [...],
      "duration_ms": 320,
      "error": null
    }
  ],
  "sources_hit": ["aleph", "opensanctions", "icij"],
  "sources_failed": ["gdelt"],
  "duration_ms": 5200,
  "created_at": "2026-03-21T15:30:00"
}
```

**Errors:**
- 404: scan_id not found

### POST /api/v1/scan/{scan_id}/refine (updated)

**Change:** Reads from SQLite database instead of in-memory store. Updates `filtered_results` in the database after refining.
