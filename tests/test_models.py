from app.models import SourceMatch, SourceResult


class TestSourceMatch:
    def test_default_data(self):
        m = SourceMatch(name='Test', type='person', summary='A test', url='http://example.com')
        assert m.data == {}

    def test_with_data(self):
        m = SourceMatch(name='Test', type='person', summary='A test', url='http://example.com', data={'key': 'val'})
        assert m.data == {'key': 'val'}


class TestSourceResult:
    def test_defaults(self):
        r = SourceResult(source='test', query='query')
        assert r.matches == []
        assert r.duration_ms == 0
        assert r.error is None

    def test_with_error(self):
        r = SourceResult(source='test', query='query', error='timeout')
        assert r.error == 'timeout'

    def test_with_matches(self):
        m = SourceMatch(name='Test', type='person', summary='A test', url='http://example.com')
        r = SourceResult(source='test', query='query', matches=[m])
        assert len(r.matches) == 1
