# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-21-audit-icij/spec.md

## Adapter Identity

| Aspect | Detail |
|---|---|
| **File** | `app/adapters/icij.py` |
| **Class** | `ICIJAdapter` extends `BaseAdapter` |
| **Adapter name** | `icij` |
| **Base URL** | `https://offshoreleaks.icij.org/api/v1` |
| **Endpoint** | `POST /reconcile` |
| **Auth** | None (free, no key required) |
| **Timeout** | 30s (inherited from BaseAdapter) |

## Query Construction

Sends a JSON body:

```json
{
  "queries": {
    "q1": {
      "query": "<query>",
      "type": "Officer"
    }
  }
}
```

- `type` is always `Officer` (hardcoded)
- Query string is sent as-is (not quoted)

## Response Parsing

Reads from `data['q1']['result']`. For each node:

| Extracted Field | Source Path | Mapped To |
|---|---|---|
| name | `name` (fallback: query) | `SourceMatch.name` |
| type | hardcoded `'officer'` | `SourceMatch.type` |
| summary | `"Score: {score:.1f} — {type joined}"` | `SourceMatch.summary` |
| url | `https://offshoreleaks.icij.org/nodes/{id}` | `SourceMatch.url` |
| data | entire `node` dict | stored as-is |

Note: the entire raw node dict is stored in `data` without selective extraction.

## kwargs Usage

None. All kwargs (`nationality`, `birth_year`, `company`, `hints`) are ignored.

## Error Handling

Inherited from BaseAdapter. Uses `resp.raise_for_status()` for HTTP errors.

## Known Limitations

- Type hardcoded to `Officer` — cannot search for `Entity` (offshore companies) or `Address` types
- No result limit parameter
- Single query per request (API supports batch via multiple keys in `queries`)
- Does not use the ICIJ search API (`GET /search?q=...`) which offers broader search
- Does not extract relationships (linked entities, intermediaries, addresses)
- Score interpretation is undocumented (varies between datasets)
- Node `type` array is joined into summary string but not used for filtering
- The raw node dict is stored but contains limited fields (id, name, score, type)

## Notable ICIJ API Capabilities Not Used

- `type: "Entity"` — search offshore companies/trusts/foundations
- `type: "Address"` — search registered addresses
- Batch reconciliation — multiple queries in single request
- `GET /search?q=...` — text-based search endpoint
- Node relationship expansion — officers → entities → intermediaries
- Dataset filtering (Panama Papers, Paradise Papers, Pandora Papers, etc.)
- Country/jurisdiction filtering
