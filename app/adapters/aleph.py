from app.adapters.base import BaseAdapter
from app.models import SourceMatch, SourceResult


class AlephAdapter(BaseAdapter):
    name = 'aleph'
    BASE_URL = 'https://aleph.occrp.org/api/2'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        async with self._client() as client:
            resp = await client.get(
                f'{self.BASE_URL}/entities',
                params={'q': f'"{query}"', 'limit': 10},
            )
            resp.raise_for_status()
            data = resp.json()

        matches = []
        for result in data.get('results', []):
            properties = result.get('properties', {})
            names = properties.get('name', [])
            name = names[0] if names else query
            schema = result.get('schema', 'Entity')
            collection = result.get('collection', {})

            matches.append(SourceMatch(
                name=name,
                type=schema.lower(),
                summary=f'{schema} in {collection.get("label", "OCCRP")}',
                url=f'https://aleph.occrp.org/entities/{result.get("id", "")}',
                data={
                    'schema': schema,
                    'properties': properties,
                    'collection': collection.get('label', ''),
                },
            ))

        return SourceResult(source=self.name, query=query, matches=matches)

    async def enrich(self, matches: list) -> list:
        async with self._client() as client:
            for match in matches:
                entity_id = match.url.split('/')[-1] if match.url else ''
                if not entity_id:
                    continue
                try:
                    resp = await client.get(f'{self.BASE_URL}/entities/{entity_id}')
                    resp.raise_for_status()
                    detail = resp.json()
                    match.data['properties'] = detail.get('properties', match.data.get('properties', {}))
                    match.data['collection'] = detail.get('collection', {}).get('label', match.data.get('collection', ''))
                    match.data['links'] = detail.get('links', {})
                except Exception:
                    pass
        return matches
