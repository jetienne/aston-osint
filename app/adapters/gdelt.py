from app.adapters.base import BaseAdapter
from app.models import SourceMatch, SourceResult


class GDELTAdapter(BaseAdapter):
    name = 'gdelt'
    BASE_URL = 'https://api.gdeltproject.org/api/v2'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        async with self._client() as client:
            resp = await client.get(
                f'{self.BASE_URL}/doc/doc',
                params={
                    'query': query,
                    'mode': 'artlist',
                    'format': 'json',
                    'maxrecords': 10,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        matches = []
        for article in data.get('articles', []):
            matches.append(SourceMatch(
                name=article.get('title', query),
                type='article',
                summary=f'{article.get("domain", "")} — {article.get("seendate", "")}',
                url=article.get('url', ''),
                data={
                    'title': article.get('title', ''),
                    'source': article.get('domain', ''),
                    'date': article.get('seendate', ''),
                    'tone': article.get('tone', ''),
                    'language': article.get('language', ''),
                },
            ))

        return SourceResult(source=self.name, query=query, matches=matches)
