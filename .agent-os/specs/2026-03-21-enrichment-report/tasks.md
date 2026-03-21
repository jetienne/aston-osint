# Spec Tasks

## Tasks

- [x] 1. Database schema + confirm endpoint
  - [x] 1.1 Write tests for new DB functions (update_scan_generating, update_scan_report_ready, get_report_pdf)
  - [x] 1.2 Add report_brief, report_pdf, report_generated_at columns to scans table
  - [x] 1.3 Implement new DB functions
  - [x] 1.4 Write tests for POST /confirm endpoint (status transitions, error cases)
  - [x] 1.5 Implement POST /api/v1/scan/{scan_id}/confirm endpoint
  - [x] 1.6 Verify all tests pass

- [x] 2. Deep enrichment pass
  - [x] 2.1 Write tests for adapter enrich() methods (Pappers, OpenSanctions, Aleph, ICIJ, GDELT)
  - [x] 2.2 Add enrich(matches) method to BaseAdapter with default no-op
  - [x] 2.3 Implement Pappers enrich — call GET /entreprise for each company siren
  - [x] 2.4 Implement OpenSanctions enrich — call GET /entities/{id} for full entity
  - [x] 2.5 Implement Aleph enrich — call GET /entities/{id} for full properties
  - [x] 2.6 Implement ICIJ enrich — fetch connected entities for each node
  - [x] 2.7 Implement GDELT enrich — re-query with 50 articles, 12-month timespan
  - [x] 2.8 Write tests for enrichment orchestration (parallel fan-out)
  - [x] 2.9 Implement run_enrichment() in orchestrator
  - [x] 2.10 Verify all tests pass

- [x] 3. Claude synthesis
  - [x] 3.1 Write tests for synthesis prompt construction and response parsing
  - [x] 3.2 Create synthesis prompt template
  - [x] 3.3 Implement synthesize_brief() — send enriched data to Claude, parse structured response
  - [x] 3.4 Handle Claude errors gracefully (fallback to raw data summary)
  - [x] 3.5 Verify all tests pass

- [x] 4. PDF report generation
  - [x] 4.1 Add WeasyPrint to requirements.txt
  - [x] 4.2 Create HTML report Jinja2 template (identity, corporate, sanctions, offshore, press, risk)
  - [x] 4.3 Write tests for PDF generation (template renders, PDF bytes produced)
  - [x] 4.4 Implement generate_pdf(brief) function
  - [x] 4.5 Write tests for GET /report and GET /brief endpoints
  - [x] 4.6 Implement GET /api/v1/scans/{scan_id}/report (PDF download)
  - [x] 4.7 Implement GET /api/v1/scans/{scan_id}/brief (JSON)
  - [x] 4.8 Verify all tests pass

- [x] 5. UI integration
  - [x] 5.1 Add "Generate Report" button after disambiguation in index.html
  - [x] 5.2 Implement confirm + poll logic (POST /confirm, poll until report_ready)
  - [x] 5.3 Show progress indicator during enrichment/generation
  - [x] 5.4 Show "Download Report" link when report_ready
  - [x] 5.5 Add report download button to scan detail in history.html
  - [ ] 5.6 Manual browser test of full flow
