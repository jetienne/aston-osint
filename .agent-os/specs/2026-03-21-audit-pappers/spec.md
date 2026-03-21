# Spec Requirements Document

> Spec: Audit Pappers Adapter
> Created: 2026-03-21
> Status: Planning

## Overview

Document what the Pappers adapter currently does — endpoint, query parameters, response parsing, data normalisation — to establish a baseline before improving crawling coverage.

## User Stories

### Adapter Behaviour Reference

As a developer, I want a detailed reference of what the Pappers adapter queries and extracts, so that I can identify gaps and plan improvements without re-reading adapter code.

The developer opens the audit document and sees the recherche-dirigeants endpoint, the fields extracted from each dirigeant record, and what company data is captured.

## Spec Scope

1. **Endpoint documentation** - Document the exact API endpoint, HTTP method, auth, and query parameters
2. **Response parsing audit** - Document which fields are extracted from dirigeants and entreprises and how they map to SourceMatch
3. **Gap analysis** - Document notable Pappers API capabilities that are not currently used

## Out of Scope

- Rewriting or improving the adapter code
- Adding new Pappers endpoints
- Performance benchmarking

## Expected Deliverable

1. A technical spec document with a complete audit of the Pappers adapter covering endpoint, auth, query params, response parsing, field mapping, kwargs usage, and known limitations
