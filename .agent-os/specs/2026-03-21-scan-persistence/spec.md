# Spec Requirements Document

> Spec: Scan Persistence & Async Execution
> Created: 2026-03-21
> Status: Planning

## Overview

Make scans asynchronous and persist every request in SQLite. POST /api/v1/scan returns immediately with a scan_id and status "running". The scan executes in the background and writes results to the database when complete. The UI polls for completion. Scan history is browsable in a History page.

## User Stories

### Non-Blocking Scan

As an ops team member, I want the scan to start immediately and show me progress, so that the page doesn't hang for 30 seconds waiting for all sources to respond.

I submit a name. The UI instantly shows "Scan started" with the source cards animating. The UI polls every 2 seconds. When the scan completes, the wizard questions appear (if any) or results display directly.

### Browse Past Scans

As an ops team member, I want to see a list of all scans I've run, so that I can find a previous search without re-running it.

I open the "History" page and see a list of all scans ordered by date, showing the query name, timestamp, status (running/complete/failed), number of matches, and sources hit. I click on a scan to see its full results.

### Review Scan Details

As a compliance officer, I want to view the full details of a past scan including both raw and filtered results, so that I have an auditable record of what was found and what was kept.

I click on a scan in the history list. I see the original query parameters, the unfiltered results (everything the sources returned after name matching), and the final filtered results (after entity resolution and disambiguation). This serves as a defensible compliance record.

## Spec Scope

1. **Async scan execution** — POST /api/v1/scan returns scan_id immediately, scan runs in background task
2. **SQLite database** — Single file on Docker volume, persists across restarts
3. **Scan table** — Stores query, kwargs, status (pending/running/complete/failed), raw results, filtered results, timestamps
4. **Polling endpoint** — GET /api/v1/scans/{id} returns current status and results when complete
5. **History API** — GET /api/v1/scans (list) and GET /api/v1/scans/{id} (detail)
6. **History UI** — New "History" page in sidebar with scan list and clickable detail view
7. **Replace in-memory store** — scan_store.py replaced by database

## Out of Scope

- WebSocket/SSE for real-time updates (polling is sufficient)
- Search/filter within scan history
- Delete/archive scans
- User authentication

## Expected Deliverable

1. POST /api/v1/scan returns in under 1 second with scan_id and status "running"
2. UI polls and shows results when scan completes
3. Every scan is visible in the History page with its status
4. Clicking a scan shows full details including raw and filtered results
5. Scans survive server restarts
