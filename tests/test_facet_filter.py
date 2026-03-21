from app.models import SourceMatch, SourceResult
from app.resolution.facet_filter import apply_facet_filters, apply_dismissed


def _match(name, data=None):
    return SourceMatch(name=name, type='person', summary='', url='', data=data or {})


def _result(source, matches):
    return SourceResult(source=source, query='test', matches=matches, duration_ms=100)


class TestApplyFacetFilters:
    def test_no_filters_returns_all(self):
        results = [_result('test', [_match('A'), _match('B')])]
        filtered = apply_facet_filters(results, {})
        assert len(filtered[0].matches) == 2

    def test_filter_by_country(self):
        results = [_result('test', [
            _match('A', {'properties': {'nationality': ['Russia']}}),
            _match('B', {'properties': {'nationality': ['France']}}),
            _match('C', {'properties': {'nationality': ['Russia']}}),
        ])]
        filtered = apply_facet_filters(results, {'country': ['Russia']})
        names = [m.name for m in filtered[0].matches]
        assert names == ['A', 'C']

    def test_multi_select_or_within_facet(self):
        results = [_result('test', [
            _match('A', {'properties': {'nationality': ['Russia']}}),
            _match('B', {'properties': {'nationality': ['France']}}),
            _match('C', {'properties': {'nationality': ['UAE']}}),
        ])]
        filtered = apply_facet_filters(results, {'country': ['Russia', 'France']})
        names = [m.name for m in filtered[0].matches]
        assert names == ['A', 'B']

    def test_and_across_facets(self):
        results = [_result('test', [
            _match('A', {'properties': {'nationality': ['Russia']}, 'datasets': ['ofac']}),
            _match('B', {'properties': {'nationality': ['Russia']}, 'datasets': ['eu_list']}),
            _match('C', {'properties': {'nationality': ['France']}, 'datasets': ['ofac']}),
        ])]
        filtered = apply_facet_filters(results, {'country': ['Russia'], 'dataset': ['ofac']})
        names = [m.name for m in filtered[0].matches]
        assert names == ['A']

    def test_filter_by_birth_year(self):
        results = [_result('test', [
            _match('A', {'properties': {'birthDate': ['1968']}}),
            _match('B', {'properties': {'birthDate': ['1975']}}),
        ])]
        filtered = apply_facet_filters(results, {'birth_year': ['1968']})
        assert len(filtered[0].matches) == 1
        assert filtered[0].matches[0].name == 'A'

    def test_filter_by_company(self):
        results = [_result('test', [
            _match('A', {'entreprises': [{'nom_entreprise': 'Gazprom'}]}),
            _match('B', {'entreprises': [{'nom_entreprise': 'TOTAL'}]}),
        ])]
        filtered = apply_facet_filters(results, {'company': ['Gazprom']})
        assert len(filtered[0].matches) == 1
        assert filtered[0].matches[0].name == 'A'

    def test_match_without_field_data_kept(self):
        results = [_result('test', [
            _match('A', {'properties': {'nationality': ['Russia']}}),
            _match('B', {}),
        ])]
        filtered = apply_facet_filters(results, {'country': ['Russia']})
        names = [m.name for m in filtered[0].matches]
        assert 'A' in names
        assert 'B' in names

    def test_preserves_error_results(self):
        results = [SourceResult(source='test', query='test', error='timeout')]
        filtered = apply_facet_filters(results, {'country': ['Russia']})
        assert filtered[0].error == 'timeout'

    def test_country_from_jurisdiction(self):
        results = [_result('test', [
            _match('A', {'jurisdiction': 'Russia'}),
            _match('B', {'jurisdiction': 'France'}),
        ])]
        filtered = apply_facet_filters(results, {'country': ['Russia']})
        assert len(filtered[0].matches) == 1
        assert filtered[0].matches[0].name == 'A'


class TestApplyDismissed:
    def test_no_dismissed(self):
        results = [_result('test', [_match('A'), _match('B')])]
        filtered = apply_dismissed(results, [])
        assert len(filtered[0].matches) == 2

    def test_dismiss_first(self):
        results = [_result('test', [_match('A'), _match('B'), _match('C')])]
        filtered = apply_dismissed(results, [0])
        names = [m.name for m in filtered[0].matches]
        assert names == ['B', 'C']

    def test_dismiss_last(self):
        results = [_result('test', [_match('A'), _match('B'), _match('C')])]
        filtered = apply_dismissed(results, [2])
        names = [m.name for m in filtered[0].matches]
        assert names == ['A', 'B']

    def test_dismiss_across_sources(self):
        results = [
            _result('aleph', [_match('A'), _match('B')]),
            _result('icij', [_match('C'), _match('D')]),
        ]
        # flat indices: A=0, B=1, C=2, D=3
        filtered = apply_dismissed(results, [1, 2])
        assert [m.name for m in filtered[0].matches] == ['A']
        assert [m.name for m in filtered[1].matches] == ['D']

    def test_dismiss_multiple(self):
        results = [_result('test', [_match('A'), _match('B'), _match('C')])]
        filtered = apply_dismissed(results, [0, 2])
        names = [m.name for m in filtered[0].matches]
        assert names == ['B']

    def test_preserves_error_results(self):
        results = [
            SourceResult(source='err', query='test', error='timeout'),
            _result('ok', [_match('A')]),
        ]
        filtered = apply_dismissed(results, [0])
        assert filtered[0].error == 'timeout'
        assert len(filtered[1].matches) == 0
