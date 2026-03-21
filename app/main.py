import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import OPENSANCTIONS_API_KEY, PAPPERS_API_KEY
from app.db import create_scan, get_scan, init_db, list_scans, update_filtered_results
from app.orchestrator import ADAPTERS, run_scan_background, run_scan_raw, _result_to_dict
from app.resolution.claude_resolver import resolve_entities
from app.resolution.disambiguation import extract_facets
from app.resolution.facet_filter import apply_dismissed, apply_facet_filters
from app.models import SourceMatch, SourceResult


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield


app = FastAPI(title='Aston OSINT', version='0.2.0', lifespan=lifespan)


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
        'version': '0.2.0',
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

    scan_id = create_scan(request.name.strip(), kwargs)
    asyncio.create_task(run_scan_background(scan_id, request.name.strip(), **kwargs))

    return {'scan_id': scan_id, 'status': 'pending'}


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


@app.get('/api/v1/scans')
def scans_list(limit: int = 50, offset: int = 0):
    return list_scans(limit=limit, offset=offset)


@app.get('/api/v1/scans/{scan_id}')
def scan_detail(scan_id: str):
    entry = get_scan(scan_id)
    if not entry:
        raise HTTPException(status_code=404, detail='Scan not found')
    return entry


@app.post('/api/v1/scan/{scan_id}/refine')
async def refine(scan_id: str, request: RefineRequest):
    entry = get_scan(scan_id)
    if not entry:
        raise HTTPException(status_code=404, detail='Scan not found or expired')

    raw_results_data = entry.get('raw_results', [])
    if not raw_results_data:
        raise HTTPException(status_code=400, detail='No raw results to refine')

    results = _deserialize_results(raw_results_data)
    query = entry['query']
    kwargs = entry.get('kwargs', {})

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

    update_filtered_results(scan_id, filtered, disambiguation)

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


def _deserialize_results(data):
    if not data:
        return []
    results = []
    for r in data:
        matches = [
            SourceMatch(
                name=m['name'], type=m['type'], summary=m['summary'],
                url=m['url'], data=m.get('data', {}),
                confidence=m.get('confidence'), rationale=m.get('rationale'),
            )
            for m in r.get('matches', [])
        ]
        results.append(SourceResult(
            source=r['source'], query=r['query'], matches=matches,
            duration_ms=r.get('duration_ms', 0), error=r.get('error'),
        ))
    return results
