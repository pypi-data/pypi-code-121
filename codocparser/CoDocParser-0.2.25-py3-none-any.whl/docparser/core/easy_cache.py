import time

_easy_cache = {}


def _init():
    global _easy_cache
    _easy_cache = {}


def easy_cache_set(key, value):
    if key not in _easy_cache:
        _easy_cache[key] = {"t": time.time()}
    _easy_cache[key]["value"] = value


def easy_cache_get(key, default=None):
    item = _easy_cache.get(key)
    if not item:
        return default
    if time.time() - item.get("t") > 60 * 60 * 24:
        return default

    return item.get("value")
