# Spec Requirements Document

> Spec: Audit Aleph Adapter
> Created: 2026-03-21
> Status: Planning

## Overview

Document what the OCCRP Aleph adapter currently does — endpoint, query parameters, response parsing, data normalisation — to establish a baseline before improving crawling coverage.

## User Stories

### Adapter Behaviour Reference

As a developer, I want a detailed reference of what the Aleph adapter queries and extracts, so that I can identify gaps and plan improvements without re-reading adapter code.

The developer opens the audit document and immediately sees: the exact endpoint hit, parameters sent, fields extracted, fields ignored, and result-count cap.

## Spec Scope

1. **Endpoint documentation** - Document the exact API endpoint, HTTP method, and query parameters used
2. **Response parsing audit** - Document which fields are extracted from the API response and how they map to SourceMatch
3. **Gap analysis** - Document notable Aleph API capabilities that are not currently used

## Out of Scope

- Rewriting or improving the adapter code
- Adding new endpoints or parameters
- Performance benchmarking

## Expected Deliverable

1. A technical spec document with a complete audit of the Aleph adapter covering endpoint, params, response parsing, field mapping, kwargs usage, and known limitations
