# Spec Requirements Document

> Spec: Audit GDELT Adapter
> Created: 2026-03-21
> Status: Planning

## Overview

Document what the GDELT adapter currently does — endpoint, query parameters, rate-limit handling, response parsing, data normalisation — to establish a baseline before improving crawling coverage.

## User Stories

### Adapter Behaviour Reference

As a developer, I want a detailed reference of what the GDELT adapter queries and extracts, so that I can identify gaps and plan improvements without re-reading adapter code.

The developer opens the audit document and sees the doc/doc endpoint parameters, the retry logic for rate limiting, and what article data is captured vs. available.

## Spec Scope

1. **Endpoint documentation** - Document the exact API endpoint, HTTP method, query parameters, and rate-limit handling
2. **Response parsing audit** - Document which fields are extracted from articles and how they map to SourceMatch
3. **Gap analysis** - Document notable GDELT API capabilities that are not currently used

## Out of Scope

- Rewriting or improving the adapter code
- Adding new GDELT modes or endpoints
- Performance benchmarking

## Expected Deliverable

1. A technical spec document with a complete audit of the GDELT adapter covering endpoint, params, retry logic, response parsing, field mapping, kwargs usage, and known limitations
