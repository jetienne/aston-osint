from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import OPENSANCTIONS_API_KEY, PAPPERS_API_KEY
from app.orchestrator import ADAPTERS, run_scan, run_scan_raw, _result_to_dict
from app.resolution.claude_resolver import resolve_entities
from app.resolution.disambiguation import extract_facets
from app.resolution.facet_filter import apply_dismissed, apply_facet_filters
from app.scan_store import get_scan

app = FastAPI(title='Aston OSINT', version='0.1.0')


class ScanRequest(BaseModel):
    name: str
    nationality: str | None = None
    company: str | None = None
    birth_year: int | None = None
    hints: str | None = None


class RefineRequest(BaseModel):
    filters: dict[str, list[str]] = {}
    dismissed: list[int] = []


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/api/v1/status')
def status():
    return {
        'service': 'aston-osint',
        'version': '0.1.0',
        'adapters': [
            {'name': a.name, 'available': True}
            for a in ADAPTERS
        ],
        'keys': {
            'opensanctions': bool(OPENSANCTIONS_API_KEY),
            'pappers': bool(PAPPERS_API_KEY),
        },
    }


@app.post('/api/v1/scan')
async def scan(request: ScanRequest):
    if not request.name.strip():
        raise HTTPException(status_code=400, detail='name is required')

    kwargs = {}
    if request.nationality:
        kwargs['nationality'] = request.nationality
    if request.company:
        kwargs['company'] = request.company
    if request.birth_year:
        kwargs['birth_year'] = request.birth_year

    result = await run_scan(request.name.strip(), **kwargs)
    return result


@app.post('/api/v1/scan/raw')
async def scan_raw(request: ScanRequest):
    if not request.name.strip():
        raise HTTPException(status_code=400, detail='name is required')

    kwargs = {}
    if request.nationality:
        kwargs['nationality'] = request.nationality
    if request.company:
        kwargs['company'] = request.company
    if request.birth_year:
        kwargs['birth_year'] = request.birth_year

    result = await run_scan_raw(request.name.strip(), **kwargs)
    return result


@app.post('/api/v1/scan/{scan_id}/refine')
async def refine(scan_id: str, request: RefineRequest):
    entry = get_scan(scan_id)
    if not entry:
        raise HTTPException(status_code=404, detail='Scan not found or expired')

    results = entry['raw_results']
    query = entry['query']
    kwargs = entry['kwargs']

    filtered = apply_facet_filters(results, request.filters)
    filtered = apply_dismissed(filtered, request.dismissed)

    has_matches = any(r.matches for r in filtered if r.error is None)
    if has_matches:
        try:
            merged_kwargs = {**kwargs, **{k: v for k, v in request.filters.items() if v}}
            filtered = await resolve_entities(query, filtered, **merged_kwargs)
        except Exception:
            pass

    disambiguation = extract_facets(filtered)

    sources_hit = [r.source for r in filtered if r.error is None]
    sources_failed = [r.source for r in filtered if r.error is not None]

    return {
        'scan_id': scan_id,
        'query': query,
        'sources': [_result_to_dict(r) for r in filtered],
        'sources_hit': sources_hit,
        'sources_failed': sources_failed,
        'disambiguation': disambiguation,
    }
