import time
from unittest.mock import patch

from app.scan_store import save_scan, get_scan, _scans, TTL


class TestScanStore:
    def setup_method(self):
        _scans.clear()

    def test_save_and_get(self):
        scan_id = save_scan('Irina Dunaeva', {}, [])
        entry = get_scan(scan_id)
        assert entry is not None
        assert entry['query'] == 'Irina Dunaeva'
        assert entry['raw_results'] == []

    def test_save_with_kwargs(self):
        scan_id = save_scan('Test', {'birth_year': 1975, 'nationality': 'Russia'}, [])
        entry = get_scan(scan_id)
        assert entry['kwargs']['birth_year'] == 1975
        assert entry['kwargs']['nationality'] == 'Russia'

    def test_get_nonexistent(self):
        assert get_scan('does-not-exist') is None

    def test_unique_ids(self):
        id1 = save_scan('A', {}, [])
        id2 = save_scan('B', {}, [])
        assert id1 != id2

    def test_expired_scan_returns_none(self):
        scan_id = save_scan('Test', {}, [])
        with patch('app.scan_store.time') as mock_time:
            mock_time.time.return_value = time.time() + TTL + 1
            assert get_scan(scan_id) is None

    def test_cleanup_removes_expired(self):
        _scans['old'] = {
            'query': 'old',
            'kwargs': {},
            'raw_results': [],
            'timestamp': time.time() - TTL - 1,
        }
        save_scan('new', {}, [])
        assert 'old' not in _scans

    def test_preserves_raw_results(self):
        from app.models import SourceMatch, SourceResult
        results = [
            SourceResult(
                source='test',
                query='Test',
                matches=[SourceMatch(name='A', type='person', summary='s', url='u')],
                duration_ms=100,
            ),
        ]
        scan_id = save_scan('Test', {}, results)
        entry = get_scan(scan_id)
        assert len(entry['raw_results']) == 1
        assert entry['raw_results'][0].matches[0].name == 'A'
