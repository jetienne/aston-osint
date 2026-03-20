# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2026-03-20-source-adapters/spec.md

## Endpoints

### GET /api/v1/status

**Purpose:** List all configured adapters and their availability
**Parameters:** None
**Response:**
```json
{
  "service": "aston-osint",
  "version": "0.1.0",
  "adapters": [
    { "name": "aleph", "available": true },
    { "name": "opensanctions", "available": true },
    { "name": "icij", "available": true },
    { "name": "pappers", "available": true },
    { "name": "gdelt", "available": true }
  ]
}
```
**Errors:** None — always returns 200

### POST /api/v1/scan (stub — wired in Phase 3)

**Purpose:** Run a scan across all sources (will be fully wired in Phase 3 with Claude synthesis)
**Parameters:**
```json
{
  "name": "string (required)",
  "nationality": "string (optional)",
  "company": "string (optional)",
  "hints": "string (optional)"
}
```
**Response:**
```json
{
  "query": "Viktor Vekselberg",
  "sources": [
    {
      "source": "opensanctions",
      "query": "Viktor Vekselberg",
      "matches": [
        {
          "name": "Viktor Vekselberg",
          "type": "person",
          "summary": "Sanctioned individual (OFAC, EU)",
          "url": "https://...",
          "data": {}
        }
      ],
      "duration_ms": 1200,
      "error": null
    }
  ],
  "sources_hit": ["aleph", "opensanctions", "icij", "pappers", "gdelt"],
  "sources_failed": [],
  "duration_ms": 3400
}
```
**Errors:**
- 400: Missing required `name` field
- 500: All sources failed
