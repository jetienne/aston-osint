from app.models import SourceMatch, SourceResult
from app.resolution.name_matcher import filter_results


def _make_result(source, matches):
    if isinstance(matches[0], str):
        match_list = [SourceMatch(name=name, type='person', summary='', url='') for name in matches]
    else:
        match_list = matches
    return SourceResult(
        source=source,
        query='test',
        matches=match_list,
    )


class TestFilterResults:
    def test_keeps_exact_matches(self):
        results = [_make_result('test', ['Irina Dunaeva', 'Oxana Dunaeva'])]
        filtered = filter_results('Irina Dunaeva', results)
        names = [m.name for m in filtered[0].matches]
        assert 'Irina Dunaeva' in names
        assert 'Oxana Dunaeva' not in names

    def test_keeps_reversed_order(self):
        results = [_make_result('test', ['Dunaeva, Irina'])]
        filtered = filter_results('Irina Dunaeva', results)
        assert len(filtered[0].matches) == 1

    def test_drops_wrong_first_name(self):
        results = [_make_result('test', ['Oxana Dunaeva', 'Irina Liner'])]
        filtered = filter_results('Irina Dunaeva', results)
        assert len(filtered[0].matches) == 0

    def test_preserves_error_results(self):
        error_result = SourceResult(source='test', query='test', error='timeout')
        filtered = filter_results('Irina Dunaeva', [error_result])
        assert filtered[0].error == 'timeout'

    def test_preserves_source_metadata(self):
        result = SourceResult(
            source='opensanctions',
            query='Irina Dunaeva',
            matches=[SourceMatch(name='Irina Dunaeva', type='person', summary='', url='')],
            duration_ms=500,
        )
        filtered = filter_results('Irina Dunaeva', [result])
        assert filtered[0].source == 'opensanctions'
        assert filtered[0].duration_ms == 500

    def test_multiple_sources(self):
        results = [
            _make_result('aleph', ['Irina Dunaeva', 'John Smith']),
            _make_result('icij', ['Oxana Dunaeva', 'Dunaeva Irina']),
        ]
        filtered = filter_results('Irina Dunaeva', results)
        assert len(filtered[0].matches) == 1
        assert filtered[0].matches[0].name == 'Irina Dunaeva'
        assert len(filtered[1].matches) == 1
        assert filtered[1].matches[0].name == 'Dunaeva Irina'

    def test_matches_via_alt_names_in_data(self):
        match = SourceMatch(
            name='فلاديمير بوتين',
            type='person', summary='', url='',
            data={'properties': {'name': ['فلاديمير بوتين', 'Vladimir Putin', 'Владимир Путин']}},
        )
        results = [_make_result('opensanctions', [match])]
        filtered = filter_results('Vladimir Putin', results)
        assert len(filtered[0].matches) == 1

    def test_no_match_even_with_alt_names(self):
        match = SourceMatch(
            name='Volodymyr Petin',
            type='person', summary='', url='',
            data={'properties': {'name': ['Volodymyr Petin', 'Володимир Петін']}},
        )
        results = [_make_result('opensanctions', [match])]
        filtered = filter_results('Vladimir Putin', results)
        assert len(filtered[0].matches) == 0
