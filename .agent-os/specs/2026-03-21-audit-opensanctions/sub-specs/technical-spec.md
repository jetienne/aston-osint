# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-21-audit-opensanctions/spec.md

## Adapter Identity

| Aspect | Detail |
|---|---|
| **File** | `app/adapters/opensanctions.py` |
| **Class** | `OpenSanctionsAdapter` extends `BaseAdapter` |
| **Adapter name** | `opensanctions` |
| **Base URL** | `https://api.opensanctions.org` |
| **Endpoint** | `POST /match/default` |
| **Auth** | Optional `Authorization: ApiKey <key>` header |
| **Env var** | `OPENSANCTIONS_API_KEY` |
| **Timeout** | 30s (inherited from BaseAdapter) |

## Query Construction

Sends a JSON body with reconciliation-style query:

```json
{
  "queries": {
    "q1": {
      "schema": "Person",
      "properties": {
        "name": ["<query>"],
        "nationality": ["<nationality>"],
        "birthDate": ["<birth_year>"]
      }
    }
  }
}
```

- `schema` is always `Person` (hardcoded)
- `nationality` added only if kwarg provided
- `birthDate` added only if `birth_year` kwarg provided (cast to string)

## Response Parsing

Reads from `data['responses']['q1']['results']`. For each result:

| Extracted Field | Source Path | Mapped To |
|---|---|---|
| name | `properties.name[]` (via `_best_latin_name`) | `SourceMatch.name` |
| type | `schema` (lowercased) | `SourceMatch.type` |
| summary | built by `_build_summary()` | `SourceMatch.summary` |
| url | `https://www.opensanctions.org/entities/{id}/` | `SourceMatch.url` |
| data.schema | `schema` | stored |
| data.score | `score` (float) | stored |
| data.properties | `properties` (full dict) | stored |
| data.datasets | `datasets` (array of strings) | stored |

## Helper Functions

### `_best_latin_name(names, fallback)`
Picks the first name in the list that starts with a Latin character (`[A-Za-z]`). Falls back to first name in list, then to `fallback`. Handles Cyrillic/Arabic names appearing first.

### `_build_summary(properties, datasets, score)`
Builds a summary string combining:
1. First `description` (if any)
2. Birth date, gender, nationality (pipe-separated)
3. Dataset count and match score

## kwargs Usage

| Kwarg | Used | How |
|---|---|---|
| `nationality` | YES | Added to `properties.nationality` |
| `birth_year` | YES | Added to `properties.birthDate` as string |
| `company` | NO | Ignored |
| `hints` | NO | Ignored |

## Error Handling

Inherited from BaseAdapter. Uses `resp.raise_for_status()`. If API key is not set, the adapter still works (free tier) but with rate limits.

## Known Limitations

- Schema hardcoded to `Person` — cannot search for `Company`, `Organization`, or `LegalEntity`
- No result limit parameter sent (relies on API default)
- Single query per request (API supports batch queries in the `queries` dict)
- No dataset filtering (searches all datasets in `default` collection)
- `company` kwarg is not used despite being available in input
- Does not use the `GET /search/default` endpoint for text search
- Does not request `topics` or `referents` data
- Does not use `first_seen` / `last_seen` temporal data

## Notable OpenSanctions API Capabilities Not Used

- `GET /search/default?q=...` — text search endpoint
- `schema: "Company"` / `"Organization"` — non-person entity types
- Batch queries — multiple `q1`, `q2`, ... in single request
- Dataset-specific matching (`/match/{dataset}`) — e.g. sanctions-only
- Topics filtering (PEP, sanctions, crime, etc.)
- `GET /entities/{id}` — full entity details
- `properties.address`, `properties.idNumber` — additional matching properties
