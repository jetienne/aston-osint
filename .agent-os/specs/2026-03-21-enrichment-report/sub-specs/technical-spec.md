# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-21-enrichment-report/spec.md

## The 3-Step Pipeline

The existing flow covers steps 1-2. This spec adds step 3.

```
Step 1: SEARCH        POST /api/v1/scan → fan-out to 5 sources → raw results
                      (already built)

Step 2: CONFIRM       Disambiguation wizard → user filters/dismisses → refine endpoint
                      The remaining matches ARE the confirmed identity.
                      (already built)

Step 3: ENRICH+REPORT POST /api/v1/scan/{scan_id}/confirm → deep enrichment → Claude synthesis → PDF
                      (this spec)
```

## Confirm Endpoint

`POST /api/v1/scan/{scan_id}/confirm`

This endpoint:
1. Reads the current filtered_results from the scan (these are the confirmed matches)
2. Triggers an async background task for enrichment + report generation
3. Returns immediately with `{"status": "generating"}`

New scan statuses: `complete` → `generating` → `report_ready`

The UI polls `GET /api/v1/scans/{scan_id}` and watches for `report_ready` status.

## Deep Enrichment Pass

Each adapter gets an `enrich(matches)` method that takes matches previously returned by that adapter and fetches deeper data. This runs in parallel across all sources.

### Per-Adapter Enrichment

**Pappers** (already partially built):
- For each person match: no additional enrichment needed (data already rich)
- For each company in the person's entreprises list: call `GET /entreprise?siren=...` to get beneficial ownership, financials, actes, BODACC
- Already has `_enrich_company()` method — extend to work on confirmed matches

**OpenSanctions**:
- For each confirmed entity: call `GET /entities/{entity_id}` to get full entity details
- Pull: all aliases, all nationalities, all birth dates, full dataset list, related entities, sanction program details
- The entity ID is already stored in `match.data` (from the URL: `/entities/{id}/`)

**Aleph**:
- For each confirmed entity: call `GET /entities/{entity_id}` to get full properties
- Pull: all properties, related entities, source documents, collection details
- The entity ID is already in the match URL

**ICIJ**:
- For each confirmed officer: call `GET /nodes/{node_id}` (if available)
- Pull: connected entities, jurisdictions, intermediaries
- Node ID is stored in `match.data['id']`

**GDELT**:
- Re-query with confirmed name, expand to 50 articles, extend timespan to 12 months
- Pull: full article list with tone analysis, source diversity

### Enrichment Orchestration

```python
async def run_enrichment(scan_id: str, confirmed_results: list[SourceResult]):
    update_scan_status(scan_id, 'generating')

    # Fan-out enrichment per source
    tasks = []
    for result in confirmed_results:
        adapter = get_adapter_by_name(result.source)
        if adapter and result.matches:
            tasks.append(adapter.enrich(result.matches))

    enriched = await asyncio.gather(*tasks, return_exceptions=True)

    # Claude synthesis
    brief = await synthesize_brief(query, enriched)

    # PDF generation
    pdf_bytes = generate_pdf(brief)

    # Store
    save_report(scan_id, brief, pdf_bytes)
    update_scan_status(scan_id, 'report_ready')
```

## Claude Synthesis

Send all enriched data to Claude with a structured prompt. The response must follow the intelligence brief JSON schema.

### Prompt Structure

```
You are an intelligence analyst producing a UHNW prospect brief.

Given the following enriched data from multiple OSINT sources, produce a structured
intelligence brief. Be factual — cite sources. Flag uncertainties.

CONFIRMED IDENTITY:
{name, birth date, nationality, companies from confirmed matches}

SOURCE DATA:
{enriched data per source}

Produce a JSON response with these sections:
- identity: name, aliases, birth date, nationalities, addresses
- corporate_network: companies, roles, beneficial ownership, financials
- sanctions_pep: any sanctions, PEP listings, watchlist entries, with programs and dates
- offshore: offshore entities, jurisdictions, intermediaries
- press_coverage: key articles, sentiment, notable events
- risk_assessment: overall risk level (LOW/MEDIUM/HIGH/CRITICAL), factors, summary
```

### Brief JSON Schema

```json
{
  "subject_name": "string",
  "generated_at": "ISO8601",
  "identity": {
    "full_name": "string",
    "aliases": ["string"],
    "birth_date": "string",
    "nationalities": ["string"],
    "addresses": ["string"]
  },
  "corporate_network": [
    {
      "company_name": "string",
      "siren": "string",
      "role": "string",
      "status": "string",
      "beneficial_ownership_pct": "number|null",
      "financials": {}
    }
  ],
  "sanctions_pep": [
    {
      "source": "string",
      "program": "string",
      "listed_since": "string",
      "details": "string"
    }
  ],
  "offshore": [
    {
      "entity_name": "string",
      "jurisdiction": "string",
      "role": "string",
      "dataset": "string"
    }
  ],
  "press_coverage": [
    {
      "title": "string",
      "source": "string",
      "date": "string",
      "url": "string",
      "sentiment": "string"
    }
  ],
  "risk_assessment": {
    "level": "LOW|MEDIUM|HIGH|CRITICAL",
    "factors": ["string"],
    "summary": "string"
  },
  "sources_consulted": ["string"],
  "data_gaps": ["string"]
}
```

## HTML Report Template

A Jinja2 template that renders the brief JSON into a professional PDF layout.

Sections:
- Header: Aston logo, report title, subject name, generation date, confidentiality notice
- Identity Summary: table with name, aliases, birth date, nationalities
- Corporate Network: table of companies with roles, ownership, financials
- Sanctions & PEP Exposure: list with source, program, details
- Offshore Connections: table with entities, jurisdictions, roles
- Press Coverage: list of articles with links and sentiment
- Risk Assessment: prominent box with level (color-coded), factors, summary
- Footer: sources consulted, data gaps, generation timestamp

## PDF Generation

Use WeasyPrint to render the HTML template to PDF.

```python
from weasyprint import HTML

def generate_pdf(brief: dict) -> bytes:
    html = render_template('report.html', brief=brief)
    return HTML(string=html).write_pdf()
```

Store the PDF bytes in the database (new column `report_pdf BLOB`) or in a file on the data volume.

## Database Changes

Add columns to the scans table:
- `report_brief TEXT` — JSON intelligence brief from Claude
- `report_pdf BLOB` — PDF bytes (or file path if stored on disk)
- `report_generated_at TEXT` — ISO8601 timestamp

Update status enum: pending → running → complete → generating → report_ready | report_failed

## API Changes

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/scan/{scan_id}/confirm` | POST | Freeze confirmed identity, trigger enrichment + report |
| `/api/v1/scans/{scan_id}/report` | GET | Download PDF (returns 404 if not ready, PDF bytes if ready) |
| `/api/v1/scans/{scan_id}` | GET | Existing — now includes `report_generated_at` and `report_status` |

## UI Changes

### index.html (scan page)
- After disambiguation wizard completes and results are displayed:
  - Show "Generate Report" button
  - On click: POST /confirm, show progress indicator ("Enriching data... Generating report...")
  - Poll scan status until `report_ready`
  - Show "Download Report (PDF)" link

### history.html (scan detail)
- If scan has `report_ready` status: show "Download Report" button
- Report generation timestamp displayed

## External Dependencies

- **WeasyPrint** — HTML-to-PDF rendering (already listed in tech-stack.md)
- **Jinja2** — HTML template rendering (comes with FastAPI/Starlette)
