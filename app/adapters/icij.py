from app.adapters.base import BaseAdapter
from app.models import SourceMatch, SourceResult


class ICIJAdapter(BaseAdapter):
    name = 'icij'
    BASE_URL = 'https://offshoreleaks.icij.org/api/v1'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        body = {
            'queries': {
                'q1': {
                    'query': query,
                    'type': 'Officer',
                },
            },
        }

        async with self._client() as client:
            resp = await client.post(
                f'{self.BASE_URL}/reconcile',
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()

        matches = []
        query_results = data.get('q1', {}).get('result', [])

        for node in query_results:
            name = node.get('name', query)
            score = node.get('score', 0)
            node_id = node.get('id', '')
            node_type = ', '.join(node.get('type', []))

            matches.append(SourceMatch(
                name=name,
                type='officer',
                summary=f'Score: {score:.1f} — {node_type}',
                url=f'https://offshoreleaks.icij.org/nodes/{node_id}',
                data=node,
            ))

        return SourceResult(source=self.name, query=query, matches=matches)
