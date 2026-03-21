# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2026-03-21-enrichment-report/spec.md

## Endpoints

### POST /api/v1/scan/{scan_id}/confirm

**Purpose:** Freeze the confirmed identity from filtered_results and trigger async enrichment + report generation.

**Parameters:**
- `scan_id` (path) — UUID of an existing scan with status `complete`

**Request Body:** None (uses the current filtered_results as the confirmed identity)

**Response:**
```json
{
  "scan_id": "uuid",
  "status": "generating"
}
```

**Errors:**
- 404: Scan not found
- 400: Scan not in `complete` status (must finish disambiguation first)
- 400: No filtered results to confirm
- 409: Report already generating or ready

**Side effects:**
- Updates scan status to `generating`
- Spawns background task: enrichment → Claude synthesis → PDF generation
- On success: status becomes `report_ready`
- On failure: status becomes `report_failed`, error stored

---

### GET /api/v1/scans/{scan_id}/report

**Purpose:** Download the generated PDF intelligence brief.

**Parameters:**
- `scan_id` (path) — UUID of a scan with status `report_ready`

**Response:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="aston-osint-{query}-{date}.pdf"`
- Body: PDF bytes

**Errors:**
- 404: Scan not found
- 404: Report not yet generated (status is not `report_ready`)

---

### GET /api/v1/scans/{scan_id}/brief

**Purpose:** Return the raw intelligence brief JSON (for API consumers or the Aston Rails integration).

**Parameters:**
- `scan_id` (path) — UUID of a scan with status `report_ready`

**Response:**
```json
{
  "subject_name": "Jean Dupont",
  "generated_at": "2026-03-21T14:30:00Z",
  "identity": { ... },
  "corporate_network": [ ... ],
  "sanctions_pep": [ ... ],
  "offshore": [ ... ],
  "press_coverage": [ ... ],
  "risk_assessment": { ... },
  "sources_consulted": [ ... ],
  "data_gaps": [ ... ]
}
```

**Errors:**
- 404: Scan not found or report not ready

---

### GET /api/v1/scans/{scan_id} (updated)

**Existing endpoint** — now includes additional fields:

```json
{
  "scan_id": "uuid",
  "query": "Jean Dupont",
  "status": "report_ready",
  "report_generated_at": "2026-03-21T14:30:00Z",
  ...existing fields...
}
```

New status values: `generating`, `report_ready`, `report_failed`
