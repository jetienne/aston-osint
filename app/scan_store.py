import time
import uuid

_scans = {}
TTL = 3600


def save_scan(query, kwargs, raw_results):
    scan_id = str(uuid.uuid4())
    _scans[scan_id] = {
        'query': query,
        'kwargs': kwargs,
        'raw_results': raw_results,
        'timestamp': time.time(),
    }
    _cleanup_expired()
    return scan_id


def get_scan(scan_id):
    entry = _scans.get(scan_id)
    if entry and time.time() - entry['timestamp'] < TTL:
        return entry
    return None


def _cleanup_expired():
    now = time.time()
    expired = [k for k, v in _scans.items() if now - v['timestamp'] >= TTL]
    for k in expired:
        del _scans[k]
