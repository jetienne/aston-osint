import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.adapters.pappers import PappersAdapter


def _mock_response(json_data, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


DIRIGEANT_RESPONSE = {
    'resultats': [
        {
            'nom': 'Dupont',
            'prenom': 'Jean',
            'qualite': 'Directeur',
            'date_de_naissance': '1980-03-15',
            'date_de_naissance_formate': '15/03/1980',
            'adresse_ligne_1': '10 rue de la Paix',
            'ville': 'Paris',
            'code_postal': '75001',
            'pays': 'France',
            'entreprises': [
                {
                    'nom_entreprise': 'Acme SAS',
                    'siren': '123456789',
                    'forme_juridique': 'SAS',
                    'domaine_activite': 'Tech',
                    'libelle_code_naf': 'Programmation informatique',
                    'siege': {'ville': 'Paris'},
                },
            ],
        },
    ],
}

COMPANY_RESPONSE = {
    'resultats': [
        {
            'nom_entreprise': 'Acme SAS',
            'siren': '123456789',
            'siege': {
                'adresse_ligne_1': '10 rue de la Paix',
                'ville': 'Paris',
                'code_postal': '75001',
            },
            'forme_juridique': 'SAS',
            'dirigeants': [
                {'nom': 'Dupont', 'prenom': 'Jean', 'qualite': 'Directeur'},
            ],
            'domaine_activite': 'Tech',
            'libelle_code_naf': 'Programmation informatique',
        },
    ],
}


class TestPappersSearchDirigeants:
    @pytest.mark.asyncio
    async def test_basic_dirigeant_search(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(DIRIGEANT_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Jean Dupont')

        assert result.source == 'pappers'
        assert len(result.matches) == 1
        assert result.matches[0].name == 'Jean Dupont'
        assert result.matches[0].type == 'person'

    @pytest.mark.asyncio
    async def test_missing_api_key(self):
        adapter = PappersAdapter()
        with patch('app.adapters.pappers.PAPPERS_API_KEY', ''):
            result = await adapter._search('Jean Dupont')

        assert result.error == 'PAPPERS_API_KEY not configured'

    @pytest.mark.asyncio
    async def test_dirigeant_url_contains_slug(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(DIRIGEANT_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Jean Dupont')

        assert 'jean_dupont' in result.matches[0].url

    @pytest.mark.asyncio
    async def test_entreprises_in_data(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(DIRIGEANT_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Jean Dupont')

        data = result.matches[0].data
        assert len(data['entreprises']) == 1
        assert data['entreprises'][0]['siren'] == '123456789'


class TestPappersCompanySearch:
    @pytest.mark.asyncio
    async def test_company_kwarg_triggers_recherche(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(COMPANY_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            await adapter._search('Acme', company=True)

        mock_client.get.assert_called_once()
        call_url = mock_client.get.call_args[0][0]
        assert '/recherche' in call_url
        assert '/recherche-dirigeants' not in call_url

    @pytest.mark.asyncio
    async def test_company_result_type_is_company(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(COMPANY_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Acme', company=True)

        assert len(result.matches) >= 1
        assert result.matches[0].type == 'company'
        assert result.matches[0].name == 'Acme SAS'

    @pytest.mark.asyncio
    async def test_company_url_uses_siren(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(COMPANY_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Acme', company=True)

        assert '123456789' in result.matches[0].url

    @pytest.mark.asyncio
    async def test_company_data_includes_siren_and_siege(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(COMPANY_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Acme', company=True)

        data = result.matches[0].data
        assert data['siren'] == '123456789'
        assert 'siege' in data

    @pytest.mark.asyncio
    async def test_default_search_without_company_kwarg_uses_dirigeants(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(DIRIGEANT_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            await adapter._search('Jean Dupont')

        call_url = mock_client.get.call_args[0][0]
        assert '/recherche-dirigeants' in call_url


class TestPappersMergedSearch:
    @pytest.mark.asyncio
    async def test_merged_results_contain_both_types(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(DIRIGEANT_RESPONSE),
            _mock_response(COMPANY_RESPONSE),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Dupont', company=True, merge=True)

        types = {m.type for m in result.matches}
        assert 'person' in types
        assert 'company' in types

    @pytest.mark.asyncio
    async def test_merged_results_calls_both_endpoints(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(DIRIGEANT_RESPONSE),
            _mock_response(COMPANY_RESPONSE),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            await adapter._search('Dupont', company=True, merge=True)

        assert mock_client.get.call_count == 2


class TestPappersDirigeantRichData:
    @pytest.mark.asyncio
    async def test_date_naissance_extracted(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(DIRIGEANT_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Jean Dupont')

        data = result.matches[0].data
        assert data['date_de_naissance'] == '1980-03-15'
        assert data['date_de_naissance_formate'] == '15/03/1980'

    @pytest.mark.asyncio
    async def test_address_extracted(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(DIRIGEANT_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Jean Dupont')

        data = result.matches[0].data
        assert data['adresse_ligne_1'] == '10 rue de la Paix'
        assert data['ville'] == 'Paris'
        assert data['code_postal'] == '75001'
        assert data['pays'] == 'France'

    @pytest.mark.asyncio
    async def test_missing_birth_date_defaults_empty(self):
        response = {
            'resultats': [{
                'nom': 'Martin',
                'prenom': 'Pierre',
                'qualite': 'Gerant',
                'entreprises': [],
            }],
        }
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Pierre Martin')

        data = result.matches[0].data
        assert data['date_de_naissance'] == ''
        assert data['date_de_naissance_formate'] == ''


COMPANY_DETAIL_RESPONSE = {
    'siren': '123456789',
    'nom_entreprise': 'Acme SAS',
    'forme_juridique': 'SAS',
    'siege': {
        'adresse_ligne_1': '10 rue de la Paix',
        'ville': 'Paris',
        'code_postal': '75001',
    },
    'beneficiaires_effectifs': [
        {
            'nom': 'Dupont',
            'prenom': 'Jean',
            'pourcentage_parts': 51.0,
        },
    ],
    'finances': [
        {
            'annee': 2024,
            'chiffre_affaires': 1500000,
            'resultat': 200000,
        },
    ],
}


class TestPappersCompanyDetails:
    @pytest.mark.asyncio
    async def test_company_search_enriches_with_details(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(COMPANY_RESPONSE),
            _mock_response(COMPANY_DETAIL_RESPONSE),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Acme', company=True, enrich=True)

        data = result.matches[0].data
        assert 'beneficiaires_effectifs' in data
        assert data['beneficiaires_effectifs'][0]['pourcentage_parts'] == 51.0

    @pytest.mark.asyncio
    async def test_company_enrichment_includes_financials(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(COMPANY_RESPONSE),
            _mock_response(COMPANY_DETAIL_RESPONSE),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Acme', company=True, enrich=True)

        data = result.matches[0].data
        assert 'finances' in data
        assert data['finances'][0]['chiffre_affaires'] == 1500000

    @pytest.mark.asyncio
    async def test_company_detail_calls_entreprise_endpoint(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(COMPANY_RESPONSE),
            _mock_response(COMPANY_DETAIL_RESPONSE),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            await adapter._search('Acme', company=True, enrich=True)

        assert mock_client.get.call_count == 2
        detail_call_url = mock_client.get.call_args_list[1][0][0]
        assert '/entreprise' in detail_call_url

    @pytest.mark.asyncio
    async def test_company_without_enrich_skips_details(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(COMPANY_RESPONSE)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Acme', company=True)

        assert mock_client.get.call_count == 1
        assert 'beneficiaires_effectifs' not in result.matches[0].data


DIRIGEANT_PAGE_1 = {
    'resultats': [
        {'nom': 'Dupont', 'prenom': 'Jean', 'qualite': 'Directeur', 'entreprises': []},
    ],
    'total': 15,
}

DIRIGEANT_PAGE_2 = {
    'resultats': [
        {'nom': 'Martin', 'prenom': 'Pierre', 'qualite': 'Gerant', 'entreprises': []},
    ],
    'total': 15,
}


class TestPappersPagination:
    @pytest.mark.asyncio
    async def test_single_page_by_default(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _mock_response(DIRIGEANT_PAGE_1)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            await adapter._search('Dupont')

        assert mock_client.get.call_count == 1

    @pytest.mark.asyncio
    async def test_max_pages_fetches_multiple(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(DIRIGEANT_PAGE_1),
            _mock_response(DIRIGEANT_PAGE_2),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Dupont', max_pages=2)

        assert mock_client.get.call_count == 2
        assert len(result.matches) == 2
        names = {m.name for m in result.matches}
        assert 'Jean Dupont' in names
        assert 'Pierre Martin' in names

    @pytest.mark.asyncio
    async def test_pagination_sends_page_param(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(DIRIGEANT_PAGE_1),
            _mock_response(DIRIGEANT_PAGE_2),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            await adapter._search('Dupont', max_pages=2)

        page_params = [
            call.kwargs.get('params', {}).get('page') or call[1].get('params', {}).get('page')
            for call in mock_client.get.call_args_list
        ]
        assert 1 in page_params
        assert 2 in page_params

    @pytest.mark.asyncio
    async def test_pagination_stops_when_no_more_results(self):
        empty_page = {'resultats': [], 'total': 1}
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(DIRIGEANT_PAGE_1),
            _mock_response(empty_page),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Dupont', max_pages=5)

        assert mock_client.get.call_count == 2
        assert len(result.matches) == 1


COMPANY_DETAIL_WITH_PUBLICATIONS = {
    'siren': '123456789',
    'nom_entreprise': 'Acme SAS',
    'beneficiaires_effectifs': [],
    'finances': [],
    'actes': [
        {
            'date_acte': '2023-06-15',
            'type': 'Statuts constitutifs',
        },
    ],
    'bodacc': [
        {
            'date_parution': '2023-07-01',
            'type': 'creation',
            'description': 'Immatriculation',
        },
    ],
}


class TestPappersLegalPublications:
    @pytest.mark.asyncio
    async def test_enrich_extracts_actes(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(COMPANY_RESPONSE),
            _mock_response(COMPANY_DETAIL_WITH_PUBLICATIONS),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Acme', company=True, enrich=True)

        data = result.matches[0].data
        assert 'actes' in data
        assert data['actes'][0]['type'] == 'Statuts constitutifs'

    @pytest.mark.asyncio
    async def test_enrich_extracts_bodacc(self):
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(COMPANY_RESPONSE),
            _mock_response(COMPANY_DETAIL_WITH_PUBLICATIONS),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Acme', company=True, enrich=True)

        data = result.matches[0].data
        assert 'bodacc' in data
        assert data['bodacc'][0]['type'] == 'creation'

    @pytest.mark.asyncio
    async def test_no_publications_when_absent(self):
        detail_no_pubs = {
            'siren': '123456789',
            'nom_entreprise': 'Acme SAS',
        }
        adapter = PappersAdapter()
        mock_client = AsyncMock()
        mock_client.get.side_effect = [
            _mock_response(COMPANY_RESPONSE),
            _mock_response(detail_no_pubs),
        ]
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch.object(adapter, '_client', return_value=mock_client), \
             patch('app.adapters.pappers.PAPPERS_API_KEY', 'test-key'):
            result = await adapter._search('Acme', company=True, enrich=True)

        data = result.matches[0].data
        assert 'actes' not in data
        assert 'bodacc' not in data
