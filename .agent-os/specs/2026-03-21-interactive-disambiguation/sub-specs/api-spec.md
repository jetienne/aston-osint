# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2026-03-21-interactive-disambiguation/spec.md

## Endpoints

### POST /api/v1/scan (updated)

**Purpose:** Run a scan and return results with disambiguation facets
**Parameters:**
```json
{
  "name": "string (required)",
  "nationality": "string (optional)",
  "company": "string (optional)",
  "birth_year": "number (optional)",
  "hints": "string (optional)"
}
```
**Response:**
```json
{
  "scan_id": "uuid",
  "query": "Vladimir Ivanov",
  "sources": [...],
  "sources_hit": [...],
  "sources_failed": [...],
  "duration_ms": 4500,
  "disambiguation": {
    "has_ambiguous": true,
    "facets": [
      {"field": "country", "label": "Country", "options": ["Russia", "France", "UAE"]},
      {"field": "birth_year", "label": "Birth year", "options": ["1968", "1975", "1982"]},
      {"field": "company", "label": "Company", "options": ["Gazprom", "Renova Group", "TOTAL SA"]}
    ]
  }
}
```

### POST /api/v1/scan/{scan_id}/refine

**Purpose:** Re-filter matches using facet selections and manual dismissals
**Parameters:**
```json
{
  "filters": {
    "country": ["Russia", "France"],
    "birth_year": ["1968"],
    "company": ["Gazprom"]
  },
  "dismissed": [2, 5]
}
```

- `filters`: multi-select values from facets. All values are arrays. Matches are kept if they match ANY selected value within a facet (OR), and must match across all active facets (AND).
- `dismissed`: array of flat match indices to remove (0-based across all sources)

**Response:** Same format as POST /api/v1/scan with updated matches, confidence scores, and rationale. Includes updated `disambiguation.facets` reflecting the remaining matches.

**Errors:**
- 404: scan_id not found or expired (TTL 1 hour)
- 400: invalid filters format
