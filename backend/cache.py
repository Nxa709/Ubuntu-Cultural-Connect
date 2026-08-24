"""Minimal in-process TTL cache for read-heavy endpoints.

Safe for a single backend worker. TTL + size caps keep memory bounded.
Not shared across multiple uvicorn workers (use Redis there if needed).
"""
import time
from threading import Lock

_MAX_ITEMS = 500

_cache: dict = {}
_lock = Lock()


def get(key):
    with _lock:
        item = _cache.get(key)
        if item is None:
            return None
        value, expires_at = item
        if time.time() > expires_at:
            del _cache[key]
            return None
        return value


def set(key, value, ttl_seconds):
    with _lock:
        if len(_cache) >= _MAX_ITEMS:
            _cache.clear()
        _cache[key] = (value, time.time() + ttl_seconds)


def clear():
    with _lock:
        _cache.clear()
