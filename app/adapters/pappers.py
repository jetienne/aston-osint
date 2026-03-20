from app.adapters.base import BaseAdapter
from app.config import PAPPERS_API_KEY
from app.models import SourceMatch, SourceResult


class PappersAdapter(BaseAdapter):
    name = 'pappers'
    BASE_URL = 'https://api.pappers.fr/v2'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        if not PAPPERS_API_KEY:
            return SourceResult(source=self.name, query=query, error='PAPPERS_API_KEY not configured')

        async with self._client() as client:
            resp = await client.get(
                f'{self.BASE_URL}/recherche',
                params={'q': query, 'par_page': 10},
                headers={'api-key': PAPPERS_API_KEY},
            )
            resp.raise_for_status()
            data = resp.json()

        matches = []
        for company in data.get('resultats', []):
            siren = company.get('siren', '')
            name = company.get('nom_entreprise', query)
            forme = company.get('forme_juridique', '')
            dirigeants = company.get('dirigeants', [])
            beneficiaires = company.get('beneficiaires_effectifs', [])

            dirigeant_names = [d.get('nom_complet', '') for d in dirigeants[:5]]

            matches.append(SourceMatch(
                name=name,
                type='company',
                summary=f'{forme} — SIREN: {siren}, dirigeants: {", ".join(dirigeant_names)}',
                url=f'https://www.pappers.fr/entreprise/{siren}',
                data={
                    'siren': siren,
                    'forme_juridique': forme,
                    'dirigeants': dirigeants[:5],
                    'beneficiaires': beneficiaires[:5],
                },
            ))

        return SourceResult(source=self.name, query=query, matches=matches)
