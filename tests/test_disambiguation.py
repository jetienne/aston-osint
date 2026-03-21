from app.models import SourceMatch, SourceResult
from app.resolution.disambiguation import extract_facets, _extract_year


def _match(name, data=None, confidence=None):
    return SourceMatch(
        name=name, type='person', summary='', url='',
        data=data or {}, confidence=confidence,
    )


def _result(matches):
    return SourceResult(source='test', query='test', matches=matches)


class TestExtractYear:
    def test_full_date(self):
        assert _extract_year('1968-05-12') == '1968'

    def test_year_only(self):
        assert _extract_year('1975') == '1975'

    def test_invalid(self):
        assert _extract_year('abc') is None

    def test_too_old(self):
        assert _extract_year('1800') is None

    def test_too_young(self):
        assert _extract_year('2020') is None

    def test_integer(self):
        assert _extract_year(1968) == '1968'


class TestExtractFacets:
    def test_no_matches_returns_empty_facets(self):
        result = extract_facets([_result([])])
        assert result['facets'] == []
        assert result['has_ambiguous'] is False

    def test_single_country_no_facet(self):
        results = [_result([
            _match('A', {'properties': {'nationality': ['Russia']}}),
            _match('B', {'properties': {'nationality': ['Russia']}}),
        ])]
        facets = extract_facets(results)['facets']
        assert not any(f['field'] == 'country' for f in facets)

    def test_two_countries_creates_facet(self):
        results = [_result([
            _match('A', {'properties': {'nationality': ['Russia']}}),
            _match('B', {'properties': {'nationality': ['France']}}),
        ])]
        facets = extract_facets(results)['facets']
        country_facet = next(f for f in facets if f['field'] == 'country')
        assert 'Russia' in country_facet['options']
        assert 'France' in country_facet['options']

    def test_birth_year_from_properties(self):
        results = [_result([
            _match('A', {'properties': {'birthDate': ['1968']}}),
            _match('B', {'properties': {'birthDate': ['1975-03-21']}}),
        ])]
        facets = extract_facets(results)['facets']
        year_facet = next(f for f in facets if f['field'] == 'birth_year')
        assert '1968' in year_facet['options']
        assert '1975' in year_facet['options']

    def test_companies_from_entreprises(self):
        results = [_result([
            _match('A', {'entreprises': [{'nom_entreprise': 'Gazprom'}]}),
            _match('B', {'entreprises': [{'nom_entreprise': 'TOTAL SA'}]}),
        ])]
        facets = extract_facets(results)['facets']
        company_facet = next(f for f in facets if f['field'] == 'company')
        assert 'Gazprom' in company_facet['options']
        assert 'TOTAL SA' in company_facet['options']

    def test_no_dataset_facet(self):
        results = [_result([
            _match('A', {'datasets': ['ofac', 'eu_sanctions']}),
            _match('B', {'datasets': ['un_sanctions']}),
        ])]
        facets = extract_facets(results)['facets']
        assert not any(f['field'] == 'dataset' for f in facets)

    def test_has_ambiguous_true_with_medium(self):
        results = [_result([_match('A', confidence='MEDIUM')])]
        assert extract_facets(results)['has_ambiguous'] is True

    def test_has_ambiguous_true_with_low(self):
        results = [_result([_match('A', confidence='LOW')])]
        assert extract_facets(results)['has_ambiguous'] is True

    def test_has_ambiguous_false_with_high_only(self):
        results = [_result([_match('A', confidence='HIGH')])]
        assert extract_facets(results)['has_ambiguous'] is False

    def test_has_ambiguous_false_with_no_confidence(self):
        results = [_result([_match('A')])]
        assert extract_facets(results)['has_ambiguous'] is False

    def test_multiple_sources(self):
        results = [
            _result([_match('A', {'properties': {'nationality': ['Russia']}})]),
            _result([_match('B', {'properties': {'nationality': ['France']}})]),
        ]
        facets = extract_facets(results)['facets']
        country_facet = next(f for f in facets if f['field'] == 'country')
        assert len(country_facet['options']) == 2

    def test_country_from_data_level(self):
        results = [_result([
            _match('A', {'jurisdiction': 'Russia'}),
            _match('B', {'jurisdiction': 'France'}),
        ])]
        facets = extract_facets(results)['facets']
        country_facet = next(f for f in facets if f['field'] == 'country')
        assert 'Russia' in country_facet['options']

    def test_ignores_empty_values(self):
        results = [_result([
            _match('A', {'properties': {'nationality': ['']}}),
            _match('B', {'properties': {'nationality': ['France']}}),
        ])]
        facets = extract_facets(results)['facets']
        assert not any(f['field'] == 'country' for f in facets)

    def test_options_are_sorted(self):
        results = [_result([
            _match('A', {'properties': {'nationality': ['France']}}),
            _match('B', {'properties': {'nationality': ['Australia']}}),
            _match('C', {'properties': {'nationality': ['Belgium']}}),
        ])]
        facets = extract_facets(results)['facets']
        country_facet = next(f for f in facets if f['field'] == 'country')
        assert country_facet['options'] == ['Australia', 'Belgium', 'France']
