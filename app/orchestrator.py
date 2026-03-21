import asyncio
import logging
import time

from app.adapters.aleph import AlephAdapter
from app.adapters.gdelt import GDELTAdapter
from app.adapters.icij import ICIJAdapter
from app.adapters.opensanctions import OpenSanctionsAdapter
from app.adapters.pappers import PappersAdapter
from app.models import SourceResult
from app.resolution.claude_resolver import resolve_entities
from app.resolution.disambiguation import extract_facets
from app.resolution.name_matcher import filter_results
from app.scan_store import save_scan

logger = logging.getLogger(__name__)

ADAPTERS = [
    AlephAdapter(),
    OpenSanctionsAdapter(),
    ICIJAdapter(),
    PappersAdapter(),
    GDELTAdapter(),
]


async def run_scan(query: str, **kwargs) -> dict:
    start = time.monotonic()

    tasks = [adapter.search(query, **kwargs) for adapter in ADAPTERS]
    raw_results: list[SourceResult] = await asyncio.gather(*tasks)

    raw_match_count = sum(len(r.matches) for r in raw_results)
    logger.info(f'Scan "{query}": {raw_match_count} raw matches from sources')

    # Pass 1: fast local name filtering
    name_filtered = filter_results(query, raw_results)
    filtered_count = sum(len(r.matches) for r in name_filtered)
    logger.info(f'Scan "{query}": {filtered_count} matches after name filter (dropped {raw_match_count - filtered_count})')

    # Save for later refinement (before Claude pass)
    scan_id = save_scan(query, kwargs, name_filtered)

    # Pass 2: Claude entity resolution for remaining matches
    has_matches = any(r.matches for r in name_filtered if r.error is None)
    if has_matches:
        try:
            results = await resolve_entities(query, name_filtered, **kwargs)
            resolved_count = sum(len(r.matches) for r in results)
            logger.info(f'Scan "{query}": {resolved_count} matches after Claude resolution')
        except Exception as e:
            logger.error(f'Scan "{query}": Claude resolution failed: {e}')
            results = name_filtered
    else:
        results = name_filtered

    sources_hit = [r.source for r in results if r.error is None]
    sources_failed = [r.source for r in results if r.error is not None]

    disambiguation = extract_facets(results)

    return {
        'scan_id': scan_id,
        'query': query,
        'sources': [_result_to_dict(r) for r in results],
        'sources_hit': sources_hit,
        'sources_failed': sources_failed,
        'duration_ms': int((time.monotonic() - start) * 1000),
        'disambiguation': disambiguation,
    }


async def run_scan_raw(query: str, **kwargs) -> dict:
    start = time.monotonic()

    tasks = [adapter.search(query, **kwargs) for adapter in ADAPTERS]
    raw_results: list[SourceResult] = await asyncio.gather(*tasks)

    sources_hit = [r.source for r in raw_results if r.error is None]
    sources_failed = [r.source for r in raw_results if r.error is not None]

    return {
        'query': query,
        'sources': [_result_to_dict(r) for r in raw_results],
        'sources_hit': sources_hit,
        'sources_failed': sources_failed,
        'duration_ms': int((time.monotonic() - start) * 1000),
    }


def _result_to_dict(r: SourceResult) -> dict:
    return {
        'source': r.source,
        'query': r.query,
        'matches': [
            {
                'name': m.name,
                'type': m.type,
                'summary': m.summary,
                'url': m.url,
                'data': m.data,
                'confidence': m.confidence,
                'rationale': m.rationale,
            }
            for m in r.matches
        ],
        'duration_ms': r.duration_ms,
        'error': r.error,
    }
