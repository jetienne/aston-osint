# Spec Requirements Document

> Spec: Scan Persistence
> Created: 2026-03-21
> Status: Planning

## Overview

Persist every scan request in a SQLite database, storing the original query, unfiltered results (raw from sources), and filtered results (after entity resolution). Display scan history as a list with a detail view for each scan.

## User Stories

### Browse Past Scans

As an ops team member, I want to see a list of all scans I've run, so that I can find a previous search without re-running it.

I open the "History" page and see a list of all scans ordered by date, showing the query name, timestamp, number of matches, and sources hit. I click on a scan to see its full results.

### Review Scan Details

As a compliance officer, I want to view the full details of a past scan including both raw and filtered results, so that I have an auditable record of what was found and what was kept.

I click on a scan in the history list. I see the original query parameters, the unfiltered results (everything the sources returned after name matching), and the final filtered results (after entity resolution and disambiguation). This serves as a defensible compliance record.

### Scan History Replaces In-Memory Store

As a developer, I want the database to replace the in-memory scan store, so that scans survive server restarts and the refine endpoint works reliably.

The current `scan_store.py` uses a dict with 1-hour TTL. The database replaces this with permanent storage. The refine endpoint reads from the database instead of memory.

## Spec Scope

1. **SQLite database** — Single file database stored on the server, persists across container restarts via a Docker volume
2. **Scan table** — Stores query, kwargs, raw results (JSON), filtered results (JSON), timestamps, metadata
3. **History API** — GET /api/v1/scans (list) and GET /api/v1/scans/:id (detail)
4. **History UI** — New "History" page in the sidebar showing scan list with clickable detail view
5. **Replace in-memory store** — scan_store.py replaced by database reads/writes

## Out of Scope

- Search/filter within scan history
- Delete/archive scans
- Export scan history
- User authentication (all scans visible to all users)

## Expected Deliverable

1. Every scan is persisted and visible in the History page
2. Clicking a scan shows full details including raw and filtered results
3. The refine endpoint reads from the database instead of memory
4. Scans survive server restarts
