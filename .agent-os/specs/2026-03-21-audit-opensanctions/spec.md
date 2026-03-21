# Spec Requirements Document

> Spec: Audit OpenSanctions Adapter
> Created: 2026-03-21
> Status: Planning

## Overview

Document what the OpenSanctions adapter currently does — endpoint, query construction, response parsing, data normalisation — to establish a baseline before improving crawling coverage.

## User Stories

### Adapter Behaviour Reference

As a developer, I want a detailed reference of what the OpenSanctions adapter queries and extracts, so that I can identify gaps and plan improvements without re-reading adapter code.

The developer opens the audit document and immediately sees: the exact endpoint hit, JSON body structure, fields extracted, helper functions, and auth method.

## Spec Scope

1. **Endpoint documentation** - Document the exact API endpoint, HTTP method, auth, and query body construction
2. **Response parsing audit** - Document which fields are extracted and how they map to SourceMatch, including helper functions
3. **Gap analysis** - Document notable OpenSanctions API capabilities that are not currently used

## Out of Scope

- Rewriting or improving the adapter code
- Adding new endpoints or schema types
- Performance benchmarking

## Expected Deliverable

1. A technical spec document with a complete audit of the OpenSanctions adapter covering endpoint, auth, query body, response parsing, helper functions, kwargs usage, and known limitations
