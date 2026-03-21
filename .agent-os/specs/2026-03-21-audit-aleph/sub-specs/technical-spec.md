# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-21-audit-aleph/spec.md

## Adapter Identity

| Aspect | Detail |
|---|---|
| **File** | `app/adapters/aleph.py` |
| **Class** | `AlephAdapter` extends `BaseAdapter` |
| **Adapter name** | `aleph` |
| **Base URL** | `https://aleph.occrp.org/api/2` |
| **Endpoint** | `GET /entities` |
| **Auth** | None (free, no key required) |
| **Timeout** | 30s (inherited from BaseAdapter) |

## Query Construction

| Parameter | Value | Notes |
|---|---|---|
| `q` | `"<query>"` | Wrapped in double quotes for exact match |
| `limit` | `10` | Hardcoded |

No other query parameters are sent. The query string is always quoted.

## Response Parsing

Iterates `data['results']` array. For each result:

| Extracted Field | Source Path | Mapped To |
|---|---|---|
| name | `properties.name[0]` (fallback: query) | `SourceMatch.name` |
| type | `schema` (lowercased) | `SourceMatch.type` |
| summary | `"{schema} in {collection.label}"` | `SourceMatch.summary` |
| url | `https://aleph.occrp.org/entities/{id}` | `SourceMatch.url` |
| data.schema | `schema` | stored in data dict |
| data.properties | `properties` (full dict) | stored in data dict |
| data.collection | `collection.label` | stored in data dict |

## kwargs Usage

None. All kwargs (`nationality`, `birth_year`, `company`, `hints`) are ignored.

## Error Handling

Inherited from BaseAdapter: any exception is caught and returned as `SourceResult(error=...)`. Uses `resp.raise_for_status()` for HTTP errors.

## Known Limitations

- Hard limit of 10 results, no pagination
- No entity type filtering (returns all schema types: Person, Company, LegalEntity, etc.)
- No use of Aleph's `filter:` parameters (collection, schema, country)
- Quoted exact-match query only — no fuzzy or phonetic search
- Does not use Aleph's cross-referencing or collection-specific search endpoints
- Does not filter by country or jurisdiction
- `company` kwarg could be used to refine search but is ignored

## Notable Aleph API Capabilities Not Used

- `GET /entities/{id}` — fetch full entity with all properties
- `filter:schemata` — restrict to Person, Company, etc.
- `filter:collection_id` — search within specific collections/datasets
- `filter:countries` — geographic filtering
- `GET /collections` — list available datasets
- Cross-reference matching (`POST /collections/{id}/xref`)
- Pagination via `offset` parameter
- Entity expansion (linked entities, relationships)
