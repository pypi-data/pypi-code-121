"""Utils for caching functions."""
import json
from functools import wraps

from utils.cache_impl import (DEFAULT_CACHE_NAME, DEFAULT_DIR, DEFAULT_TIMEOUT,
                              _Cache)


def cache(
    cache_name=DEFAULT_CACHE_NAME, timeout=DEFAULT_TIMEOUT, dir=DEFAULT_DIR
):
    """Wrap class Cache as decorator."""

    def cache_inner(func):
        @wraps(func)
        def cache_inner_inner(*args, **kwargs):
            cache_key = json.dumps(
                {
                    'cache_name': cache_name,
                    'function_name': func.__name__,
                    'kwargs': kwargs,
                    'args': args,
                }
            )

            def fallback():
                return func(*args, **kwargs)

            return _Cache(cache_name, timeout, dir).get(cache_key, fallback)

        return cache_inner_inner

    return cache_inner
