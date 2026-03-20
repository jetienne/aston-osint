from app.adapters.base import BaseAdapter
from app.models import SourceMatch, SourceResult


class ICIJAdapter(BaseAdapter):
    name = 'icij'
    BASE_URL = 'https://offshoreleaks.icij.org/api/v1'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        async with self._client() as client:
            resp = await client.get(
                f'{self.BASE_URL}/search',
                params={'q': query, 'limit': 10},
            )
            resp.raise_for_status()
            data = resp.json()

        matches = []
        results = data if isinstance(data, list) else data.get('results', data.get('data', []))

        for node in results:
            if isinstance(node, dict):
                name = node.get('name', node.get('entity', query))
                node_type = node.get('type', node.get('node_type', 'entity'))
                jurisdiction = node.get('jurisdiction', node.get('country_codes', ''))
                source_id = node.get('sourceID', node.get('source', ''))

                matches.append(SourceMatch(
                    name=name,
                    type=node_type.lower() if isinstance(node_type, str) else 'entity',
                    summary=f'{node_type} — jurisdiction: {jurisdiction}, source: {source_id}',
                    url=f'https://offshoreleaks.icij.org/nodes/{node.get("id", node.get("node_id", ""))}',
                    data=node,
                ))

        return SourceResult(source=self.name, query=query, matches=matches)
