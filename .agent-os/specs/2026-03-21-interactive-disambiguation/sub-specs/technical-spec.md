# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-21-interactive-disambiguation/spec.md

## Technical Requirements

### Scan State Storage

Store raw scan results in memory with a TTL of 1 hour. Each scan gets a UUID.

```python
# app/scan_store.py
import time
import uuid

scans = {}  # scan_id -> {query, kwargs, raw_results, timestamp}
TTL = 3600  # 1 hour

def save_scan(query, kwargs, raw_results):
    scan_id = str(uuid.uuid4())
    scans[scan_id] = {
        'query': query,
        'kwargs': kwargs,
        'raw_results': raw_results,
        'timestamp': time.time(),
    }
    cleanup_expired()
    return scan_id

def get_scan(scan_id):
    entry = scans.get(scan_id)
    if entry and time.time() - entry['timestamp'] < TTL:
        return entry
    return None

def cleanup_expired():
    now = time.time()
    expired = [k for k, v in scans.items() if now - v['timestamp'] >= TTL]
    for k in expired:
        del scans[k]
```

### Updated Scan Flow

1. POST /api/v1/scan runs sources + entity resolution as before
2. Raw results (pre-filtering) are stored in scan_store with a scan_id
3. Response includes scan_id so the UI can call refine later

```json
{
  "scan_id": "abc-123",
  "query": "Vladimir Ivanov",
  "sources": [...],
  "disambiguation": {
    "has_ambiguous": true,
    "facets": [
      {
        "field": "country",
        "label": "Country",
        "options": ["Russia", "France", "UAE"]
      },
      {
        "field": "birth_year",
        "label": "Birth year",
        "options": ["1968", "1975", "1982"]
      },
      {
        "field": "company",
        "label": "Company",
        "options": ["Gazprom", "Renova Group", "TOTAL SA"]
      }
    ]
  },
  ...
}
```

### Disambiguation Facets

No Claude call needed — facets are extracted directly from the match data. The system scans all matches and collects distinct values for key fields (country, birth year, company, datasets/sources). Only facets with 2+ distinct values are shown (no point filtering if all matches share the same country).

```python
# app/resolution/disambiguation.py

def extract_facets(results: list[SourceResult]) -> list[dict]:
    """Extract selectable filter facets from match data."""
    countries = set()
    birth_years = set()
    companies = set()
    datasets = set()

    for result in results:
        for match in result.matches:
            data = match.data
            # Extract from different source formats
            for key in ('nationality', 'country', 'jurisdiction', 'country_codes'):
                val = data.get(key)
                if val:
                    countries.update(val if isinstance(val, list) else [val])

            for key in ('birthDate', 'birth_year', 'date_naissance'):
                val = data.get(key)
                if val:
                    birth_years.update(val if isinstance(val, list) else [str(val)])

            for key in ('entreprises', 'companies'):
                items = data.get(key, [])
                for item in items:
                    name = item.get('nom_entreprise') or item.get('name')
                    if name:
                        companies.add(name)

            for ds in data.get('datasets', []):
                datasets.add(ds)

    facets = []
    if len(countries) >= 2:
        facets.append({'field': 'country', 'label': 'Country', 'options': sorted(countries)})
    if len(birth_years) >= 2:
        facets.append({'field': 'birth_year', 'label': 'Birth year', 'options': sorted(birth_years)})
    if len(companies) >= 2:
        facets.append({'field': 'company', 'label': 'Company', 'options': sorted(companies)})
    if len(datasets) >= 2:
        facets.append({'field': 'dataset', 'label': 'Dataset', 'options': sorted(datasets)})

    return facets
```

### Refine Endpoint

```
POST /api/v1/scan/{scan_id}/refine
```

Request body:
```json
{
  "filters": {
    "country": "Russia",
    "birth_year": "1968",
    "company": "Gazprom"
  },
  "dismissed": [0, 3]
}
```

- `filters`: values selected from facets — used to filter matches that don't match the selection
- `dismissed`: list of flat match indices the user manually rejected

The endpoint:
1. Retrieves raw results (post name-filter, pre-Claude) from scan_store
2. Applies facet filters: keep only matches whose data contains the selected values
3. Removes dismissed matches
4. Re-runs Claude entity resolution with the filtered set + enriched context
5. Returns updated results with revised confidence scores

### Match Cards UI

Each match renders as a card with:
- Name, type, source, summary
- Confidence badge (HIGH green / MEDIUM orange / LOW red)
- Claude's rationale
- Source link
- Accept button (confirms the match — sets confidence to HIGH)
- Dismiss button (removes the match from results)

When dismissed, the match index is tracked and sent to the refine endpoint.

### Disambiguation Facets UI

Above the results, a row of multi-select pill groups shows the available facets. All facets are multi-select — the user can pick multiple values (e.g. two birth years if unsure, or "Russia" + "France" if the person operates in both). All pills start unselected (no filter). Toggling a pill auto-submits (debounced 500ms) by calling POST /api/v1/scan/{scan_id}/refine with the accumulated filters. Matches are kept if they match ANY of the selected values for a given facet (OR within a facet, AND across facets).

### File Structure

```
app/
├── scan_store.py           # in-memory scan storage with TTL
├── resolution/
│   ├── disambiguation.py   # question generation via Claude
│   └── ...
```

### API Changes Summary

| Endpoint | Change |
|---|---|
| POST /api/v1/scan | Returns scan_id + disambiguation questions |
| POST /api/v1/scan/{scan_id}/refine | New — re-evaluate with additional context |
