from app.adapters.base import BaseAdapter
from app.config import PAPPERS_API_KEY
from app.models import SourceMatch, SourceResult


class PappersAdapter(BaseAdapter):
    name = 'pappers'
    BASE_URL = 'https://api.pappers.fr/v2'

    async def _search(self, query: str, **kwargs) -> SourceResult:
        if not PAPPERS_API_KEY:
            return SourceResult(source=self.name, query=query, error='PAPPERS_API_KEY not configured')

        company = kwargs.get('company', False)
        merge = kwargs.get('merge', False)
        enrich = kwargs.get('enrich', False)
        max_pages = kwargs.get('max_pages', 1)

        matches = []

        async with self._client() as client:
            if merge:
                matches += await self._search_dirigeants(client, query, max_pages)
                matches += await self._search_companies(client, query, max_pages)
            elif company:
                matches += await self._search_companies(client, query, max_pages)
            else:
                matches += await self._search_dirigeants(client, query, max_pages)

            if enrich:
                for match in matches:
                    siren = match.data.get('siren', '')
                    if siren:
                        await self._enrich_company(client, match, siren)

        return SourceResult(source=self.name, query=query, matches=matches)

    async def _search_dirigeants(self, client, query: str, max_pages: int = 1) -> list[SourceMatch]:
        matches = []
        for page in range(1, max_pages + 1):
            resp = await client.get(
                f'{self.BASE_URL}/recherche-dirigeants',
                params={'q': query, 'par_page': 10, 'page': page, 'api_token': PAPPERS_API_KEY},
            )
            resp.raise_for_status()
            data = resp.json()

            resultats = data.get('resultats', [])
            if not resultats:
                break

            for dirigeant in resultats:
                nom = dirigeant.get('nom', '')
                prenom = dirigeant.get('prenom', '')
                full_name = f'{prenom} {nom}'.strip() or query
                qualite = dirigeant.get('qualite', '')
                entreprises = dirigeant.get('entreprises', [])

                company_names = [e.get('nom_entreprise', '') for e in entreprises[:3]]

                slug = f'{prenom}_{nom}'.lower().strip('_')
                date_naissance = dirigeant.get('date_de_naissance') or ''
                if date_naissance and len(date_naissance) >= 7:
                    slug = f'{slug}_{date_naissance[:7]}'
                url = f'https://www.pappers.fr/dirigeant/{slug}' if slug else ''

                matches.append(SourceMatch(
                    name=full_name,
                    type='person',
                    summary=f'{qualite} — {", ".join(company_names)}',
                    url=url,
                    data={
                        'nom': nom,
                        'prenom': prenom,
                        'qualite': qualite,
                        'date_de_naissance': dirigeant.get('date_de_naissance', '') or '',
                        'date_de_naissance_formate': dirigeant.get('date_de_naissance_formate', '') or '',
                        'adresse_ligne_1': dirigeant.get('adresse_ligne_1', '') or '',
                        'ville': dirigeant.get('ville', '') or '',
                        'code_postal': dirigeant.get('code_postal', '') or '',
                        'pays': dirigeant.get('pays', '') or '',
                        'entreprises': [
                            {
                                'nom_entreprise': e.get('nom_entreprise', ''),
                                'siren': e.get('siren', ''),
                                'forme_juridique': e.get('forme_juridique', ''),
                                'domaine_activite': e.get('domaine_activite', ''),
                                'libelle_code_naf': e.get('libelle_code_naf', ''),
                                'siege': e.get('siege', {}),
                            }
                            for e in entreprises[:5]
                        ],
                    },
                ))
        return matches

    async def _enrich_company(self, client, match: SourceMatch, siren: str):
        resp = await client.get(
            f'{self.BASE_URL}/entreprise',
            params={'siren': siren, 'api_token': PAPPERS_API_KEY},
        )
        resp.raise_for_status()
        detail = resp.json()

        beneficiaires = detail.get('beneficiaires_effectifs', [])
        if beneficiaires:
            match.data['beneficiaires_effectifs'] = beneficiaires

        finances = detail.get('finances', [])
        if finances:
            match.data['finances'] = finances

        actes = detail.get('actes', [])
        if actes:
            match.data['actes'] = actes

        bodacc = detail.get('bodacc', [])
        if bodacc:
            match.data['bodacc'] = bodacc

    async def _search_companies(self, client, query: str, max_pages: int = 1) -> list[SourceMatch]:
        matches = []
        for page in range(1, max_pages + 1):
            resp = await client.get(
                f'{self.BASE_URL}/recherche',
                params={'q': query, 'par_page': 10, 'page': page, 'api_token': PAPPERS_API_KEY},
            )
            resp.raise_for_status()
            data = resp.json()

            resultats = data.get('resultats', [])
            if not resultats:
                break

            for company in resultats:
                nom = company.get('nom_entreprise', '')
                siren = company.get('siren', '')
                siege = company.get('siege', {})
                forme = company.get('forme_juridique', '')
                domaine = company.get('domaine_activite', '')
                naf = company.get('libelle_code_naf', '')
                dirigeants = company.get('dirigeants', [])

                dirigeant_names = [
                    f'{d.get("prenom", "")} {d.get("nom", "")}'.strip()
                    for d in dirigeants[:3]
                ]
                url = f'https://www.pappers.fr/entreprise/{siren}' if siren else ''

                matches.append(SourceMatch(
                    name=nom or query,
                    type='company',
                    summary=f'{forme} — {", ".join(dirigeant_names)}',
                    url=url,
                    data={
                        'siren': siren,
                        'nom_entreprise': nom,
                        'forme_juridique': forme,
                        'domaine_activite': domaine,
                        'libelle_code_naf': naf,
                        'siege': siege,
                        'dirigeants': [
                            {
                                'nom': d.get('nom', ''),
                                'prenom': d.get('prenom', ''),
                                'qualite': d.get('qualite', ''),
                            }
                            for d in dirigeants[:5]
                        ],
                    },
                ))
        return matches
