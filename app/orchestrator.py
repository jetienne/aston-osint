import asyncio
import time

from app.adapters.aleph import AlephAdapter
from app.adapters.gdelt import GDELTAdapter
from app.adapters.icij import ICIJAdapter
from app.adapters.opensanctions import OpenSanctionsAdapter
from app.adapters.pappers import PappersAdapter
from app.models import SourceResult

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
    results: list[SourceResult] = await asyncio.gather(*tasks)

    sources_hit = [r.source for r in results if r.error is None]
    sources_failed = [r.source for r in results if r.error is not None]

    return {
        'query': query,
        'sources': [_result_to_dict(r) for r in results],
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
            }
            for m in r.matches
        ],
        'duration_ms': r.duration_ms,
        'error': r.error,
    }
