import json
import os
import sqlite3
import uuid
from dataclasses import asdict
from datetime import datetime, timezone


DB_PATH = os.environ.get('DB_PATH', '/data/aston-osint.db')


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = _connect()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            query TEXT NOT NULL,
            kwargs TEXT NOT NULL DEFAULT '{}',
            status TEXT NOT NULL DEFAULT 'pending',
            raw_results TEXT,
            filtered_results TEXT,
            disambiguation TEXT,
            sources_hit TEXT NOT NULL DEFAULT '[]',
            sources_failed TEXT NOT NULL DEFAULT '[]',
            duration_ms INTEGER DEFAULT 0,
            error TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


def create_scan(query, kwargs):
    scan_id = str(uuid.uuid4())
    conn = _connect()
    conn.execute(
        'INSERT INTO scans (id, query, kwargs, status, created_at) VALUES (?, ?, ?, ?, ?)',
        (scan_id, query, json.dumps(kwargs), 'pending', _now()),
    )
    conn.commit()
    conn.close()
    return scan_id


def update_scan_running(scan_id):
    conn = _connect()
    conn.execute('UPDATE scans SET status = ? WHERE id = ?', ('running', scan_id))
    conn.commit()
    conn.close()


def update_scan_complete(scan_id, raw_results, filtered_results, disambiguation, sources_hit, sources_failed, duration_ms):
    conn = _connect()
    conn.execute(
        '''UPDATE scans SET
            status = ?, raw_results = ?, filtered_results = ?,
            disambiguation = ?, sources_hit = ?, sources_failed = ?,
            duration_ms = ?, completed_at = ?
        WHERE id = ?''',
        (
            'complete',
            _serialize_results(raw_results),
            _serialize_results(filtered_results),
            json.dumps(disambiguation, default=str),
            json.dumps(sources_hit),
            json.dumps(sources_failed),
            duration_ms,
            _now(),
            scan_id,
        ),
    )
    conn.commit()
    conn.close()


def update_scan_failed(scan_id, error):
    conn = _connect()
    conn.execute(
        'UPDATE scans SET status = ?, error = ?, completed_at = ? WHERE id = ?',
        ('failed', str(error), _now(), scan_id),
    )
    conn.commit()
    conn.close()


def update_filtered_results(scan_id, filtered_results, disambiguation):
    conn = _connect()
    conn.execute(
        'UPDATE scans SET filtered_results = ?, disambiguation = ? WHERE id = ?',
        (_serialize_results(filtered_results), json.dumps(disambiguation, default=str), scan_id),
    )
    conn.commit()
    conn.close()


def get_scan(scan_id):
    conn = _connect()
    row = conn.execute('SELECT * FROM scans WHERE id = ?', (scan_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return _row_to_dict(row)


def list_scans(limit=50, offset=0):
    conn = _connect()
    rows = conn.execute(
        'SELECT id, query, kwargs, status, sources_hit, sources_failed, duration_ms, error, created_at, completed_at, filtered_results FROM scans ORDER BY created_at DESC LIMIT ? OFFSET ?',
        (limit, offset),
    ).fetchall()
    total = conn.execute('SELECT COUNT(*) FROM scans').fetchone()[0]
    conn.close()

    scans = []
    for row in rows:
        entry = {
            'id': row['id'],
            'query': row['query'],
            'kwargs': json.loads(row['kwargs']),
            'status': row['status'],
            'sources_hit': json.loads(row['sources_hit']),
            'sources_failed': json.loads(row['sources_failed']),
            'duration_ms': row['duration_ms'],
            'error': row['error'],
            'created_at': row['created_at'],
            'completed_at': row['completed_at'],
        }
        filtered = row['filtered_results']
        if filtered:
            results = json.loads(filtered)
            entry['match_count'] = sum(len(r.get('matches', [])) for r in results)
        else:
            entry['match_count'] = 0
        scans.append(entry)

    return {'scans': scans, 'total': total}


def _row_to_dict(row):
    entry = {
        'id': row['id'],
        'query': row['query'],
        'kwargs': json.loads(row['kwargs']),
        'status': row['status'],
        'sources_hit': json.loads(row['sources_hit']),
        'sources_failed': json.loads(row['sources_failed']),
        'duration_ms': row['duration_ms'],
        'error': row['error'],
        'created_at': row['created_at'],
        'completed_at': row['completed_at'],
    }
    if row['raw_results']:
        entry['raw_results'] = json.loads(row['raw_results'])
    else:
        entry['raw_results'] = []
    if row['filtered_results']:
        entry['filtered_results'] = json.loads(row['filtered_results'])
    else:
        entry['filtered_results'] = []
    if row['disambiguation']:
        entry['disambiguation'] = json.loads(row['disambiguation'])
    else:
        entry['disambiguation'] = {'has_ambiguous': False, 'facets': []}
    return entry


def _now():
    return datetime.now(timezone.utc).isoformat()


def _serialize_results(results):
    if not results:
        return '[]'
    return json.dumps([_result_to_dict(r) for r in results], default=str)


def _result_to_dict(r):
    if isinstance(r, dict):
        return r
    return {
        'source': r.source,
        'query': r.query,
        'matches': [asdict(m) for m in r.matches],
        'duration_ms': r.duration_ms,
        'error': r.error,
    }
