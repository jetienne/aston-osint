# Spec Tasks

## Tasks

- [ ] 1. Database schema + confirm endpoint
  - [ ] 1.1 Write tests for new DB functions (update_scan_generating, update_scan_report_ready, get_report_pdf)
  - [ ] 1.2 Add report_brief, report_pdf, report_generated_at columns to scans table
  - [ ] 1.3 Implement new DB functions
  - [ ] 1.4 Write tests for POST /confirm endpoint (status transitions, error cases)
  - [ ] 1.5 Implement POST /api/v1/scan/{scan_id}/confirm endpoint
  - [ ] 1.6 Verify all tests pass

- [ ] 2. Deep enrichment pass
  - [ ] 2.1 Write tests for adapter enrich() methods (Pappers, OpenSanctions, Aleph, ICIJ, GDELT)
  - [ ] 2.2 Add enrich(matches) method to BaseAdapter with default no-op
  - [ ] 2.3 Implement Pappers enrich — call GET /entreprise for each company siren
  - [ ] 2.4 Implement OpenSanctions enrich — call GET /entities/{id} for full entity
  - [ ] 2.5 Implement Aleph enrich — call GET /entities/{id} for full properties
  - [ ] 2.6 Implement ICIJ enrich — fetch connected entities for each node
  - [ ] 2.7 Implement GDELT enrich — re-query with 50 articles, 12-month timespan
  - [ ] 2.8 Write tests for enrichment orchestration (parallel fan-out)
  - [ ] 2.9 Implement run_enrichment() in orchestrator
  - [ ] 2.10 Verify all tests pass

- [ ] 3. Claude synthesis
  - [ ] 3.1 Write tests for synthesis prompt construction and response parsing
  - [ ] 3.2 Create synthesis prompt template
  - [ ] 3.3 Implement synthesize_brief() — send enriched data to Claude, parse structured response
  - [ ] 3.4 Handle Claude errors gracefully (fallback to raw data summary)
  - [ ] 3.5 Verify all tests pass

- [ ] 4. PDF report generation
  - [ ] 4.1 Add WeasyPrint to requirements.txt
  - [ ] 4.2 Create HTML report Jinja2 template (identity, corporate, sanctions, offshore, press, risk)
  - [ ] 4.3 Write tests for PDF generation (template renders, PDF bytes produced)
  - [ ] 4.4 Implement generate_pdf(brief) function
  - [ ] 4.5 Write tests for GET /report and GET /brief endpoints
  - [ ] 4.6 Implement GET /api/v1/scans/{scan_id}/report (PDF download)
  - [ ] 4.7 Implement GET /api/v1/scans/{scan_id}/brief (JSON)
  - [ ] 4.8 Verify all tests pass

- [ ] 5. UI integration
  - [ ] 5.1 Add "Generate Report" button after disambiguation in index.html
  - [ ] 5.2 Implement confirm + poll logic (POST /confirm, poll until report_ready)
  - [ ] 5.3 Show progress indicator during enrichment/generation
  - [ ] 5.4 Show "Download Report" link when report_ready
  - [ ] 5.5 Add report download button to scan detail in history.html
  - [ ] 5.6 Manual browser test of full flow
