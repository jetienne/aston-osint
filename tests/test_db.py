import os
import tempfile
from unittest.mock import patch

from app.db import (
    create_scan, get_scan, init_db, list_scans,
    update_filtered_results, update_scan_complete,
    update_scan_failed, update_scan_running,
)
from app.models import SourceMatch, SourceResult


def setup_test_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    return path


class TestDb:
    def setup_method(self):
        self.db_path = setup_test_db()
        self.patcher = patch('app.db.DB_PATH', self.db_path)
        self.patcher.start()
        init_db()

    def teardown_method(self):
        self.patcher.stop()
        os.unlink(self.db_path)

    def test_create_and_get(self):
        scan_id = create_scan('Vladimir Putin', {'nationality': 'Russia'})
        entry = get_scan(scan_id)
        assert entry is not None
        assert entry['query'] == 'Vladimir Putin'
        assert entry['kwargs'] == {'nationality': 'Russia'}
        assert entry['status'] == 'pending'

    def test_get_nonexistent(self):
        assert get_scan('does-not-exist') is None

    def test_unique_ids(self):
        id1 = create_scan('A', {})
        id2 = create_scan('B', {})
        assert id1 != id2

    def test_update_running(self):
        scan_id = create_scan('Test', {})
        update_scan_running(scan_id)
        entry = get_scan(scan_id)
        assert entry['status'] == 'running'

    def test_update_complete(self):
        scan_id = create_scan('Test', {})
        results = [
            SourceResult(
                source='test', query='Test',
                matches=[SourceMatch(name='A', type='person', summary='s', url='u')],
                duration_ms=100,
            ),
        ]
        update_scan_complete(
            scan_id, results, results,
            {'has_ambiguous': False, 'facets': []},
            ['test'], [], 500,
        )
        entry = get_scan(scan_id)
        assert entry['status'] == 'complete'
        assert entry['duration_ms'] == 500
        assert entry['completed_at'] is not None
        assert len(entry['raw_results']) == 1
        assert len(entry['filtered_results']) == 1
        assert entry['raw_results'][0]['matches'][0]['name'] == 'A'

    def test_update_failed(self):
        scan_id = create_scan('Test', {})
        update_scan_failed(scan_id, 'All sources timed out')
        entry = get_scan(scan_id)
        assert entry['status'] == 'failed'
        assert entry['error'] == 'All sources timed out'

    def test_list_scans_empty(self):
        result = list_scans()
        assert result['scans'] == []
        assert result['total'] == 0

    def test_list_scans_ordered(self):
        id1 = create_scan('First', {})
        id2 = create_scan('Second', {})
        result = list_scans()
        assert result['total'] == 2
        assert result['scans'][0]['id'] == id2
        assert result['scans'][1]['id'] == id1

    def test_list_scans_pagination(self):
        for i in range(5):
            create_scan(f'Scan {i}', {})
        result = list_scans(limit=2, offset=0)
        assert len(result['scans']) == 2
        assert result['total'] == 5

    def test_list_scans_match_count(self):
        scan_id = create_scan('Test', {})
        results = [
            SourceResult(
                source='test', query='Test',
                matches=[
                    SourceMatch(name='A', type='person', summary='', url=''),
                    SourceMatch(name='B', type='person', summary='', url=''),
                ],
                duration_ms=100,
            ),
        ]
        update_scan_complete(scan_id, results, results, {}, ['test'], [], 100)
        result = list_scans()
        assert result['scans'][0]['match_count'] == 2

    def test_update_filtered_results(self):
        scan_id = create_scan('Test', {})
        results = [
            SourceResult(source='test', query='Test', matches=[], duration_ms=100),
        ]
        update_scan_complete(scan_id, results, results, {}, [], [], 100)

        new_results = [
            SourceResult(
                source='test', query='Test',
                matches=[SourceMatch(name='Filtered', type='person', summary='', url='')],
                duration_ms=100,
            ),
        ]
        update_filtered_results(scan_id, new_results, {'has_ambiguous': False, 'facets': []})

        entry = get_scan(scan_id)
        assert len(entry['filtered_results']) == 1
        assert entry['filtered_results'][0]['matches'][0]['name'] == 'Filtered'
