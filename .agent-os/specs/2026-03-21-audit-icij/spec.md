# Spec Requirements Document

> Spec: Audit ICIJ OffshoreLeaks Adapter
> Created: 2026-03-21
> Status: Planning

## Overview

Document what the ICIJ OffshoreLeaks adapter currently does — endpoint, query construction, response parsing, data normalisation — to establish a baseline before improving crawling coverage.

## User Stories

### Adapter Behaviour Reference

As a developer, I want a detailed reference of what the ICIJ adapter queries and extracts, so that I can identify gaps and plan improvements without re-reading adapter code.

The developer opens the audit document and sees the reconciliation endpoint structure, the hardcoded Officer type, and what entity data is extracted vs. available.

## Spec Scope

1. **Endpoint documentation** - Document the exact API endpoint, HTTP method, and query body construction
2. **Response parsing audit** - Document which fields are extracted and how they map to SourceMatch
3. **Gap analysis** - Document notable ICIJ API capabilities that are not currently used

## Out of Scope

- Rewriting or improving the adapter code
- Adding new entity types or endpoints
- Performance benchmarking

## Expected Deliverable

1. A technical spec document with a complete audit of the ICIJ adapter covering endpoint, query body, response parsing, field mapping, kwargs usage, and known limitations
