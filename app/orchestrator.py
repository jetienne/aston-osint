import asyncio
import logging
import time

from app.adapters.aleph import AlephAdapter
from app.adapters.gdelt import GDELTAdapter
from app.adapters.icij import ICIJAdapter
from app.adapters.opensanctions import OpenSanctionsAdapter
from app.adapters.pappers import PappersAdapter
from app.db import (
    update_scan_complete, update_scan_failed, update_scan_generating,
    update_scan_report_failed, update_scan_report_ready, update_scan_running,
)
from app.models import SourceResult
from app.report import generate_pdf
from app.resolution.claude_resolver import resolve_entities
from app.resolution.disambiguation import extract_facets
from app.resolution.name_matcher import filter_results
from app.synthesis import synthesize_brief

logger = logging.getLogger(__name__)

ADAPTERS = [
    AlephAdapter(),
    OpenSanctionsAdapter(),
    ICIJAdapter(),
    PappersAdapter(),
    GDELTAdapter(),
]


async def run_scan_background(scan_id: str, query: str, **kwargs):
    try:
        update_scan_running(scan_id)
        start = time.monotonic()

        tasks = [adapter.search(query, **kwargs) for adapter in ADAPTERS]
        raw_results: list[SourceResult] = await asyncio.gather(*tasks)

        raw_match_count = sum(len(r.matches) for r in raw_results)
        logger.info(f'Scan "{query}": {raw_match_count} raw matches from sources')

        name_filtered = filter_results(query, raw_results)
        filtered_count = sum(len(r.matches) for r in name_filtered)
        logger.info(f'Scan "{query}": {filtered_count} matches after name filter')

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
        duration_ms = int((time.monotonic() - start) * 1000)

        update_scan_complete(
            scan_id, name_filtered, results, disambiguation,
            sources_hit, sources_failed, duration_ms,
        )
        logger.info(f'Scan "{query}" complete in {duration_ms}ms')

    except Exception as e:
        logger.error(f'Scan "{query}" failed: {e}')
        update_scan_failed(scan_id, str(e))


ADAPTER_MAP = {a.name: a for a in ADAPTERS}


async def run_report_generation(scan_id: str, query: str, confirmed_results: list[SourceResult]):
    try:
        update_scan_generating(scan_id)

        tasks = []
        for result in confirmed_results:
            adapter = ADAPTER_MAP.get(result.source)
            if adapter and result.matches:
                tasks.append(_enrich_source(adapter, result))

        enriched = await asyncio.gather(*tasks, return_exceptions=True)

        enriched_results = []
        for item in enriched:
            if isinstance(item, SourceResult):
                enriched_results.append(item)
            elif isinstance(item, Exception):
                logger.error(f'Enrichment failed: {item}')

        if not enriched_results:
            enriched_results = confirmed_results

        brief = await synthesize_brief(query, enriched_results)
        pdf_bytes = generate_pdf(brief)
        update_scan_report_ready(scan_id, brief, pdf_bytes)
        logger.info(f'Report for "{query}" generated successfully')

    except Exception as e:
        logger.error(f'Report generation for "{query}" failed: {e}')
        update_scan_report_failed(scan_id, str(e))


async def _enrich_source(adapter, result: SourceResult) -> SourceResult:
    enriched_matches = await adapter.enrich(result.matches)
    return SourceResult(
        source=result.source,
        query=result.query,
        matches=enriched_matches,
        duration_ms=result.duration_ms,
        error=result.error,
    )


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
