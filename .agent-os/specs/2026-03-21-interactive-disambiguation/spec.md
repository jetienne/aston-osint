# Spec Requirements Document

> Spec: Interactive Disambiguation
> Created: 2026-03-21
> Status: Planning

## Overview

Add an interactive disambiguation step after scan results return, allowing the user to answer clarifying questions (age, country, known associates, etc.) and manually accept or reject individual matches — even if those details weren't provided at query time.

## User Stories

### Refine Results After Scanning

As an ops team member, I want to review the scan results and answer follow-up questions to narrow them down, so that I can confirm which matches are about the right person without re-running the scan.

I search for "Vladimir Ivanov". The scan returns 8 matches across sources — some are sanctioned individuals, some are offshore company officers, some are press mentions. The system asks me: "Do you know their approximate birth year?", "Which country are they based in?", "Are they associated with any of these companies?". As I answer, irrelevant matches disappear in real-time.

### Manually Accept or Reject Matches

As a compliance officer, I want to manually keep or dismiss individual results, so that I have full control over what ends up in the final report.

After the automated filtering, I still see 3 matches. I recognise one as the wrong person (same name, different industry). I click "dismiss" on that match. The remaining 2 are confirmed for the report.

### Iterative Refinement Without Re-Scanning

As an ops team member, I don't want to re-run the full scan every time I have new information, so that I save time and API calls.

The raw results are preserved. When I provide additional context (birth year, country), Claude re-evaluates the existing matches without hitting the 5 source APIs again.

## Spec Scope

1. **Disambiguation questions** — After results load, the UI suggests clarifying questions based on what's ambiguous (birth year, country, company). User answers are sent to Claude for re-evaluation.
2. **Match cards with accept/dismiss** — Each match is displayed as a card with an accept/dismiss button. Dismissed matches are removed from the results.
3. **Re-evaluation endpoint** — POST /api/v1/scan/:id/refine that takes the original results + new context and re-runs Claude entity resolution without re-querying sources.
4. **Scan state persistence** — Store raw scan results in memory (or simple file/SQLite) so refinement doesn't require a re-scan. Scans expire after 1 hour.

## Out of Scope

- Persistent scan history beyond 1 hour (future phase)
- Batch disambiguation across multiple scans
- Auto-suggesting questions based on ML/heuristics (Claude generates them)
- Full report generation (Phase 3 — Claude synthesis)

## Expected Deliverable

1. After a scan completes, the UI shows disambiguation questions if there are MEDIUM/LOW confidence matches
2. Answering a question re-filters results in real-time without re-scanning sources
3. Each match card has accept/dismiss buttons that immediately update the results
4. The refine endpoint accepts new context and returns updated results with revised confidence
