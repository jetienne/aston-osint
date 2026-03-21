from app.adapters.base import BaseAdapter
from app.config import PAPPERS_API_KEY
from app.models import SourceMatch, SourceResult


class PappersAdapter(BaseAdapter):
    name = 'pappers'
    BASE_URL = 'https://api.pappers.fr/v2'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        if not PAPPERS_API_KEY:
            return SourceResult(source=self.name, query=query, error='PAPPERS_API_KEY not configured')

        matches = []

        async with self._client() as client:
            resp = await client.get(
                f'{self.BASE_URL}/recherche-dirigeants',
                params={'q': query, 'par_page': 10, 'api_token': PAPPERS_API_KEY},
            )
            resp.raise_for_status()
            data = resp.json()

        for dirigeant in data.get('resultats', []):
            nom = dirigeant.get('nom', '')
            prenom = dirigeant.get('prenom', '')
            full_name = f'{prenom} {nom}'.strip() or query
            qualite = dirigeant.get('qualite', '')
            entreprises = dirigeant.get('entreprises', [])

            company_names = [e.get('nom_entreprise', '') for e in entreprises[:3]]
            siren_list = [e.get('siren', '') for e in entreprises[:3]]

            matches.append(SourceMatch(
                name=full_name,
                type='person',
                summary=f'{qualite} — {", ".join(company_names)}',
                url=f'https://www.pappers.fr/entreprise/{siren_list[0]}' if siren_list else '',
                data={
                    'nom': nom,
                    'prenom': prenom,
                    'qualite': qualite,
                    'entreprises': entreprises[:3],
                },
            ))

        return SourceResult(source=self.name, query=query, matches=matches)
