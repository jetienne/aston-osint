# Spec Requirements Document

> Spec: Source Adapters
> Created: 2026-03-20
> Status: Planning

## Overview

Build async adapters for 5 OSINT data sources (OCCRP Aleph, OpenSanctions, ICIJ OffshoreLeaks, Pappers, GDELT) with a parallel orchestrator that fans out to all sources simultaneously and returns normalised results within 30 seconds.

## User Stories

### Run a Multi-Source OSINT Scan

As an ops team member, I want to submit a person or entity name and get results from all 5 data sources in a single response, so that I have a comprehensive intelligence picture without querying each source manually.

The user submits a name (and optionally a nationality and company). The orchestrator dispatches queries to all 5 sources in parallel using asyncio.gather. Each adapter has a 30-second timeout. Results are normalised into a common schema. Sources that timeout or error return an empty result with an error flag — they never block the other sources.

### Handle Partial Failures Gracefully

As a compliance officer, I want to know which sources returned results and which failed, so that I can assess the completeness of the intelligence and decide if a manual follow-up is needed.

The response includes a `sources_hit` array listing which sources returned data and which timed out or errored. A source failure never causes the entire scan to fail.

## Spec Scope

1. **Base adapter interface** — Abstract base class defining the async query method, 30s timeout, and normalised output schema
2. **OCCRP Aleph adapter** — Query the Aleph API for investigations, court records, corporate registries
3. **OpenSanctions adapter** — Query for PEP lists, sanctions (OFAC, EU, UN), watchlists
4. **ICIJ OffshoreLeaks adapter** — Query for Panama Papers, Paradise Papers, offshore entities
5. **Pappers adapter** — Query French company registries and beneficial ownership
6. **GDELT adapter** — Query global news and event monitoring for press mentions
7. **Parallel orchestrator** — Fan out to all 5 adapters via asyncio.gather, collect and merge results

## Out of Scope

- Claude AI synthesis (Phase 3)
- PDF report generation (Phase 3)
- POST /api/v1/scan endpoint wiring (Phase 3)
- Scan history or persistence
- Rate limiting or caching

## Expected Deliverable

1. Calling the orchestrator with a name returns normalised results from all 5 sources (or clean timeouts) within 30 seconds
2. Each adapter can be tested independently with a known name (e.g. "Viktor Vekselberg" for OpenSanctions)
3. The /api/v1/status endpoint lists all configured adapters and their availability
