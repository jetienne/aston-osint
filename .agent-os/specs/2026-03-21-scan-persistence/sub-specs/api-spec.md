# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2026-03-21-scan-persistence/spec.md

## Endpoints

### POST /api/v1/scan (updated — now async)

**Purpose:** Start a scan, returns immediately
**Parameters:**
```json
{
  "name": "string (required)",
  "nationality": "string (optional)",
  "company": "string (optional)",
  "birth_year": "number (optional)"
}
```
**Response (immediate):**
```json
{
  "scan_id": "uuid",
  "status": "pending"
}
```

### GET /api/v1/scans/{scan_id}

**Purpose:** Get scan status and results (used for polling and history detail)

**Response (running):**
```json
{
  "id": "uuid",
  "query": "Vladimir Putin",
  "kwargs": {"nationality": "Russia"},
  "status": "running",
  "created_at": "2026-03-21T15:30:00"
}
```

**Response (complete):**
```json
{
  "id": "uuid",
  "query": "Vladimir Putin",
  "kwargs": {"nationality": "Russia"},
  "status": "complete",
  "raw_results": [...],
  "filtered_results": [...],
  "disambiguation": { "has_ambiguous": true, "facets": [...] },
  "sources_hit": ["aleph", "opensanctions"],
  "sources_failed": ["gdelt"],
  "duration_ms": 5200,
  "created_at": "2026-03-21T15:30:00",
  "completed_at": "2026-03-21T15:30:05"
}
```

**Response (failed):**
```json
{
  "id": "uuid",
  "query": "Vladimir Putin",
  "status": "failed",
  "error": "All sources timed out",
  "created_at": "2026-03-21T15:30:00"
}
```

**Errors:**
- 404: scan_id not found

### GET /api/v1/scans

**Purpose:** List all scans, most recent first
**Parameters:**
- `limit` (query, optional, default 50)
- `offset` (query, optional, default 0)

**Response:**
```json
{
  "scans": [
    {
      "id": "uuid",
      "query": "Vladimir Putin",
      "status": "complete",
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

### POST /api/v1/scan/{scan_id}/refine (updated)

**Change:** Reads raw_results from database. Updates filtered_results in database after refining.

**Parameters:**
```json
{
  "filters": { "country": ["Russia"] },
  "dismissed": [2]
}
```

**Response:** Same as GET /api/v1/scans/{scan_id} with updated filtered_results.
