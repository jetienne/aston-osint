# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2026-03-21-enrichment-report/spec.md

## Schema Changes

Add three columns to the existing `scans` table:

```sql
ALTER TABLE scans ADD COLUMN report_brief TEXT;
ALTER TABLE scans ADD COLUMN report_pdf BLOB;
ALTER TABLE scans ADD COLUMN report_generated_at TEXT;
```

### Column Details

| Column | Type | Purpose |
|--------|------|---------|
| `report_brief` | TEXT (JSON) | Claude-generated intelligence brief as JSON |
| `report_pdf` | BLOB | WeasyPrint-rendered PDF bytes |
| `report_generated_at` | TEXT (ISO8601) | Timestamp when report was generated |

### Status Values

The existing `status` column now supports additional values:

| Status | Meaning |
|--------|---------|
| `pending` | Scan created, not yet started |
| `running` | Adapters querying sources |
| `complete` | Search done, ready for disambiguation/confirmation |
| `generating` | Enrichment + report in progress |
| `report_ready` | PDF report available for download |
| `report_failed` | Report generation failed (error column has details) |
| `failed` | Scan itself failed |

### Migration Strategy

SQLite supports `ALTER TABLE ... ADD COLUMN` — run the three ALTER statements in `init_db()` using `IF NOT EXISTS` pattern (catch the "duplicate column" error silently, or check pragma table_info first).

### New DB Functions

```python
def update_scan_generating(scan_id: str):
    """Mark scan as generating report."""

def update_scan_report_ready(scan_id: str, brief: dict, pdf_bytes: bytes):
    """Store the brief JSON and PDF bytes, set status to report_ready."""

def update_scan_report_failed(scan_id: str, error: str):
    """Mark report generation as failed."""

def get_report_pdf(scan_id: str) -> bytes | None:
    """Return PDF bytes for download, or None if not ready."""

def get_report_brief(scan_id: str) -> dict | None:
    """Return brief JSON, or None if not ready."""
```
