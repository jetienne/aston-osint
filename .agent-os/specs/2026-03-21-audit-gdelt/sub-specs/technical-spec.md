# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-21-audit-gdelt/spec.md

## Adapter Identity

| Aspect | Detail |
|---|---|
| **File** | `app/adapters/gdelt.py` |
| **Class** | `GDELTAdapter` extends `BaseAdapter` |
| **Adapter name** | `gdelt` |
| **Base URL** | `https://api.gdeltproject.org/api/v2` |
| **Endpoint** | `GET /doc/doc` |
| **Auth** | None (free, no key required) |
| **Timeout** | 30s (inherited from BaseAdapter) |

## Query Construction

| Parameter | Value | Notes |
|---|---|---|
| `query` | `"<query>"` | Wrapped in double quotes for exact match |
| `mode` | `artlist` | Returns article list |
| `format` | `json` | JSON output |
| `timespan` | `3months` | Rolling 3-month window |
| `maxrecords` | `10` | Hardcoded limit |
| `sort` | `DateDesc` | Most recent first |

## Rate Limit Handling

1. **Initial delay:** 2-second `asyncio.sleep(2)` before first request
2. **On HTTP 429:** retry up to 3 times with linear backoff:
   - Attempt 1 retry: sleep 3s
   - Attempt 2 retry: sleep 6s
   - Attempt 3 retry: sleep 9s
3. **After 3 failed retries:** returns `SourceResult(error='Rate limited after 3 retries')`

Total worst-case delay: 2s initial + 3s + 6s + 9s = 20 seconds before giving up.

## Response Parsing

Reads from `data['articles']`. For each article:

| Extracted Field | Source Path | Mapped To |
|---|---|---|
| name | `title` (fallback: query) | `SourceMatch.name` |
| type | hardcoded `'article'` | `SourceMatch.type` |
| summary | `"{domain} — {seendate}"` | `SourceMatch.summary` |
| url | `url` | `SourceMatch.url` |
| data.title | `title` | stored |
| data.source | `domain` | stored |
| data.date | `seendate` | stored |
| data.tone | `tone` | stored (raw string, not parsed) |
| data.language | `language` | stored |

## kwargs Usage

None. All kwargs (`nationality`, `birth_year`, `company`, `hints`) are ignored.

## Error Handling

- Rate limit (429): retry with backoff as described above
- Other HTTP errors: `resp.raise_for_status()` → caught by BaseAdapter
- If `data` is still `None` after retries: explicit error return

## Known Limitations

- 3-month time window hardcoded — misses older press coverage
- Max 10 articles, no pagination
- Quoted exact-match only — no fuzzy or contextual search
- 2-second initial sleep adds latency even when rate limit isn't hit
- `tone` field stored as raw semicolon-separated numeric string, not parsed into individual scores (overall, positive, negative, polarity, activity, self/group reference density)
- Does not filter by language or source country
- Does not use `sourcelang` or `sourcecountry` parameters
- `company` and `hints` kwargs could refine the query string but are ignored

## Notable GDELT API Capabilities Not Used

- **GKG mode** (`mode=artgallery` or custom GKG queries) — extracts persons, organizations, themes, locations from articles
- **Timeline mode** (`mode=timelinevol`) — volume of coverage over time
- **Tone chart** (`mode=tonechart`) — tone analysis over time
- `sourcelang` parameter — filter by article language
- `sourcecountry` parameter — filter by source country
- `theme` parameter — filter by GDELT theme taxonomy
- `domain` / `domainis` — restrict to specific news domains
- Longer `timespan` values (e.g. `12months`, `5years`)
- `maxrecords` up to 250 — get more articles per query
- `near` operator — proximity search for co-occurring terms
- `tone` operator — filter by article sentiment
