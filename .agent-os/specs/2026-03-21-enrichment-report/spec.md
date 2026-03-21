# Spec Requirements Document

> Spec: Deep Enrichment & PDF Report
> Created: 2026-03-21
> Status: Planning

## Overview

After the user confirms the target identity through the existing disambiguation flow, go back to every source that returned matches and pull the deepest data available, then feed everything to Claude for synthesis into a structured intelligence brief, and render it as a downloadable PDF.

## User Stories

### Confirm and Generate Report

As an ops staff member, I want to confirm the target after the disambiguation wizard, then click "Generate Report" so that the system enriches the confirmed matches and produces a PDF intelligence brief I can share with the sales team.

The user submits a name, the system searches all 5 sources and presents filtered results with disambiguation. The user answers the facet questions and dismisses false positives. What remains is the confirmed identity. The user clicks "Generate Report". The system takes the confirmed matches, goes back to each source for deep enrichment, sends everything to Claude for synthesis, renders an HTML template into a PDF, and returns a download link.

### Download and Share

As a sales advisor, I want to download the PDF report from the scan detail page so that I can attach it to the client file or send it to the compliance team.

## Spec Scope

1. **Confirm endpoint** — POST /api/v1/scan/{scan_id}/confirm that freezes the confirmed identity and triggers enrichment
2. **Deep enrichment pass** — orchestrator takes confirmed matches back to each source adapter for richer data (Pappers company details, OpenSanctions full entity, Aleph document details, GDELT extended articles)
3. **Claude synthesis** — send all enriched data to Claude with a prompt that produces a structured intelligence brief (identity summary, corporate network, sanctions/PEP exposure, offshore connections, press coverage, risk assessment)
4. **HTML report template** — structured layout for the intelligence brief
5. **PDF generation** — WeasyPrint renders the HTML template to PDF
6. **Download endpoint** — GET /api/v1/scans/{scan_id}/report returns the PDF
7. **UI integration** — "Generate Report" button after disambiguation, progress indicator, download link when ready

## Out of Scope

- Changing the existing search or disambiguation flow
- Adding new data sources
- Storing PDFs permanently (generate on demand or cache briefly)
- User authentication (existing API key middleware, not yet enforced)

## Expected Deliverable

1. After confirming the target via disambiguation, clicking "Generate Report" produces a downloadable PDF intelligence brief within 30 seconds
2. The PDF contains structured sections: identity, corporate network, sanctions/PEP, offshore, press, risk score
3. The report is accessible from the scan detail page in the history view
