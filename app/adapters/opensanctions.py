from app.adapters.base import BaseAdapter
from app.config import OPENSANCTIONS_API_KEY
from app.models import SourceMatch, SourceResult


class OpenSanctionsAdapter(BaseAdapter):
    name = 'opensanctions'
    BASE_URL = 'https://api.opensanctions.org'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        if not OPENSANCTIONS_API_KEY:
            return SourceResult(source=self.name, query=query, error='OPENSANCTIONS_API_KEY not configured')

        headers = {'Authorization': f'ApiKey {OPENSANCTIONS_API_KEY}'}

        async with self._client() as client:
            resp = await client.get(
                f'{self.BASE_URL}/match/default',
                params={'q': query, 'limit': 10},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        matches = []
        for result in data.get('results', []):
            score = result.get('score', 0)
            if score < 0.5:
                continue

            properties = result.get('properties', {})
            datasets = result.get('datasets', [])
            name = properties.get('name', [query])[0] if properties.get('name') else query
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
