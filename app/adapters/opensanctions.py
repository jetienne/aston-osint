import re

from app.adapters.base import BaseAdapter
from app.config import OPENSANCTIONS_API_KEY
from app.models import SourceMatch, SourceResult


def _best_latin_name(names: list, fallback: str) -> str:
    if not names:
        return fallback
    for n in names:
        if isinstance(n, str) and re.match(r'^[A-Za-z]', n):
            return n
    return names[0]


class OpenSanctionsAdapter(BaseAdapter):
    name = 'opensanctions'
    BASE_URL = 'https://api.opensanctions.org'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        headers = {}
        if OPENSANCTIONS_API_KEY:
            headers['Authorization'] = f'ApiKey {OPENSANCTIONS_API_KEY}'

        body = {
            'queries': {
                'q1': {
                    'schema': 'Person',
                    'properties': {
                        'name': [query],
                    },
                },
            },
        }

        nationality = kwargs.get('nationality')
        if nationality:
            body['queries']['q1']['properties']['nationality'] = [nationality]

        birth_year = kwargs.get('birth_year')
        if birth_year:
            body['queries']['q1']['properties']['birthDate'] = [str(birth_year)]

        async with self._client() as client:
            resp = await client.post(
                f'{self.BASE_URL}/match/default',
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        matches = []
        query_results = data.get('responses', {}).get('q1', {}).get('results', [])

        for result in query_results:
            score = result.get('score', 0)
            properties = result.get('properties', {})
            datasets = result.get('datasets', [])
            names = properties.get('name', [query])
            name = _best_latin_name(names, query)
            schema = result.get('schema', 'Entity')

            matches.append(SourceMatch(
                name=name,
                type=schema.lower(),
                summary=f'{schema} — datasets: {", ".join(datasets)} (score: {score:.2f})',
                url=f'https://www.opensanctions.org/entities/{result.get("id", "")}/',
                data={
                    'schema': schema,
                    'score': score,
                    'properties': properties,
                    'datasets': datasets,
                },
            ))

        return SourceResult(source=self.name, query=query, matches=matches)
