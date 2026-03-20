from app.adapters.base import BaseAdapter
from app.models import SourceMatch, SourceResult


class AlephAdapter(BaseAdapter):
    name = 'aleph'
    BASE_URL = 'https://aleph.occrp.org/api/2'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        async with self._client() as client:
            resp = await client.get(
                f'{self.BASE_URL}/entities',
                params={'q': query, 'limit': 10},
            )
            resp.raise_for_status()
            data = resp.json()

        matches = []
        for result in data.get('results', []):
            properties = result.get('properties', {})
            name = properties.get('name', [query])[0] if properties.get('name') else result.get('id', query)
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
