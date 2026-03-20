# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-20-source-adapters/spec.md

## Technical Requirements

### Normalised Output Schema

Every adapter returns the same structure:

```python
@dataclass
class SourceMatch:
    name: str           # matched entity name
    type: str           # "person", "company", "entity", "article"
    summary: str        # one-line description of the match
    url: str            # link to the source record
    data: dict          # source-specific raw data

@dataclass
class SourceResult:
    source: str         # adapter name (e.g. "opensanctions")
    query: str          # the original query string
    matches: list[SourceMatch]
    duration_ms: int    # how long the query took
    error: str | None   # error message if failed, None if success
```

### Base Adapter Interface

```python
class BaseAdapter(ABC):
    name: str
    timeout: float = 30.0

    @abstractmethod
    async def search(self, query: str, **kwargs) -> SourceResult:
        """Query the source and return normalised results."""
```

kwargs may include: `nationality`, `company`, `country` for sources that support filtered queries.

### Orchestrator

```python
async def run_scan(query: str, **kwargs) -> list[SourceResult]:
    adapters = [AlephAdapter(), OpenSanctionsAdapter(), ICIJAdapter(), PappersAdapter(), GDELTAdapter()]
    tasks = [adapter.search(query, **kwargs) for adapter in adapters]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Convert exceptions to SourceResult with error field
    return [handle_result(r, a) for r, a in zip(results, adapters)]
```

### Adapter Specifications

#### OCCRP Aleph
- Base URL: `https://aleph.occrp.org/api/2/`
- Endpoint: `GET /entities?q={query}`
- Auth: None required (public API)
- Response: JSON with `results` array of entity objects
- Extract: name, schema (type), properties, collection info
- Pagination: first page only (limit=10)

#### OpenSanctions
- Base URL: `https://api.opensanctions.org/`
- Endpoint: `GET /match/default?q={query}`
- Auth: API key via `Authorization` header
- Response: JSON with `results` array of entity matches with score
- Extract: name, schema, properties, datasets (which sanctions list), score
- Filter: score > 0.5 to reduce noise

#### ICIJ OffshoreLeaks
- Base URL: `https://offshoreleaks.icij.org/api/v1/`
- Endpoint: `GET /search?q={query}`
- Auth: None required
- Response: JSON with array of nodes (entities, officers, addresses)
- Extract: name, node type, jurisdiction, linked entities, source (Panama/Paradise/Pandora Papers)

#### Pappers
- Base URL: `https://api.pappers.fr/v2/`
- Endpoint: `GET /recherche?q={query}`
- Auth: API key via `api_token` query parameter
- Response: JSON with `resultats` array of company objects
- Extract: company name, SIREN, legal form, dirigeants (directors), beneficiaires (beneficial owners)
- Secondary: if company found, fetch `/entreprise?siren={siren}` for full details

#### GDELT
- Base URL: `https://api.gdeltproject.org/api/v2/`
- Endpoint: `GET /doc/doc?query={query}&mode=artlist&format=json`
- Auth: None required
- Response: JSON with `articles` array
- Extract: title, url, source name, date, tone (sentiment)
- Limit: 10 most recent articles

### File Structure

```
app/
├── __init__.py
├── main.py
├── config.py              # settings (API keys from env vars)
├── models.py              # SourceMatch, SourceResult dataclasses
├── orchestrator.py         # run_scan function
└── adapters/
    ├── __init__.py
    ├── base.py            # BaseAdapter ABC
    ├── aleph.py
    ├── opensanctions.py
    ├── icij.py
    ├── pappers.py
    └── gdelt.py
```

### Configuration

API keys loaded from environment variables:
- `OPENSANCTIONS_API_KEY`
- `PAPPERS_API_KEY`

Other sources (Aleph, ICIJ, GDELT) require no authentication.

### HTTP Client

Use `httpx.AsyncClient` with:
- 30-second timeout per request
- Connection pooling (single client instance per adapter)
- User-Agent header identifying the service

## External Dependencies

- **httpx** — Async HTTP client for source API calls
- **Justification:** FastAPI's recommended async HTTP client, supports connection pooling and timeouts natively
