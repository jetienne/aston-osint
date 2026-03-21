import asyncio

from app.adapters.base import BaseAdapter
from app.models import SourceMatch, SourceResult


class GDELTAdapter(BaseAdapter):
    name = 'gdelt'
    BASE_URL = 'https://api.gdeltproject.org/api/v2'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        await asyncio.sleep(2)

        data = None
        async with self._client() as client:
            for attempt in range(3):
                resp = await client.get(
                    f'{self.BASE_URL}/doc/doc',
                    params={
                        'query': f'"{query}"',
                        'mode': 'artlist',
                        'format': 'json',
                        'timespan': '3months',
                        'maxrecords': 10,
                        'sort': 'DateDesc',
                    },
                )
                if resp.status_code == 429:
                    await asyncio.sleep(3 * (attempt + 1))
                    continue
                resp.raise_for_status()
                data = resp.json()
                break

        if data is None:
            return SourceResult(source=self.name, query=query, error='Rate limited after 3 retries')

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

    async def enrich(self, matches: list) -> list:
        if not matches:
            return matches
        query = matches[0].data.get('title', '') or matches[0].name
        await asyncio.sleep(2)
        async with self._client() as client:
            for attempt in range(3):
                resp = await client.get(
                    f'{self.BASE_URL}/doc/doc',
                    params={
                        'query': f'"{query}"',
                        'mode': 'artlist',
                        'format': 'json',
                        'timespan': '12months',
                        'maxrecords': 50,
                        'sort': 'DateDesc',
                    },
                )
                if resp.status_code == 429:
                    await asyncio.sleep(3 * (attempt + 1))
                    continue
                resp.raise_for_status()
                data = resp.json()
                articles = data.get('articles', [])
                if articles and matches:
                    matches[0].data['enriched_articles'] = [
                        {
                            'title': a.get('title', ''),
                            'source': a.get('domain', ''),
                            'date': a.get('seendate', ''),
                            'url': a.get('url', ''),
                            'tone': a.get('tone', ''),
                            'language': a.get('language', ''),
                        }
                        for a in articles
                    ]
                break
        return matches
