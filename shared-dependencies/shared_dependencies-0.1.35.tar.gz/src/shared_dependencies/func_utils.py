import os
import contextlib
import json
from abc import ABC, abstractmethod
from typing import Optional
from shared_dependencies.sentry import safe_capture_exception
from shared_dependencies.http_client import CustomAsyncClient


def get_message_from_exception(e):
    """
    Use to avoid nested FastAPI responses when a microservices calls another one and gets an exception
    """
    if not hasattr(e, "detail"):
        return str(e)
    return e.detail if "message" not in e.detail else e.detail["message"]


@contextlib.asynccontextmanager
async def patient_httpx_client(*args, **kwargs):
    async with httpx.AsyncClient(
            *args, timeout=httpx.Timeout(10.0, connect=60.0), **kwargs
    ) as client:
        yield client


def get_openid_config_url(http_exception, url: str, app_id: Optional[str], tenant_id: Optional[str]) -> str:
    if tenant_id:
        return url.replace("common", tenant_id)
    elif app_id:
        return f"{url}?appid={app_id}"
    else:
        event_id = capture_message("No valid app_id or tenant_id provided")
        raise http_exception(
            status_code=401,
            detail={"message": "No valid app_id or tenant_id provided", "sentry_eventid": event_id},
        )


@contextlib.asynccontextmanager
async def openid_config(base_url: str, app_id: Optional[str], tenant_id: Optional[str], http_exception, status_code: int):
    # Bruno : it was my proposition to place this as a context manager in this shared_dependencies library, but both sounds now like a bad idea now
    # By both I mean the context manager as well as its location (should rather stay in athena-auth ?)
    url = get_openid_config_url(http_exception, url=base_url, app_id=app_id, tenant_id=tenant_id)
    try:
        res = await CustomAsyncClient().get(url)
        conf = res.json()
    except Exception as e:
        event_id = safe_capture_exception(e)
        raise http_exception(
            status_code=status_code,
            detail={"message": e, "sentry_eventid": event_id},
        ) from e
    yield conf


@contextlib.contextmanager
def tempenv(**update):
    """
    Temporarily updates the ``os.environ``
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    previous_values = {k: env.get(k, None) for k in update}
    for k, v in update.items():
        env[k] = v
    yield
    for k, v in previous_values.items():
        if v is None:
            # means that it was not an existing key before the updating operation
            env.pop(k)
        else:
            env[k] = v


class CachingEngine(ABC):
    @abstractmethod
    def set(self, key: str, val: str):
        pass

    @abstractmethod
    def get_cache_or_none(self, key: str):
        pass


class Cached:
    """cache a function that returns jsonifiable output"""

    def __init__(self, cache_key_func, caching_engine: CachingEngine, should_cache=None):
        self.cache_key_func = cache_key_func
        self.caching_engine = caching_engine
        self._should_cache = should_cache

    def should_cache(self, *args, **kwargs):
        if self._should_cache is None:
            return True
        else:
            return self._should_cache(*args, **kwargs)

    def __call__(self, function_to_be_decorated):
        def new_func(*args, **kwargs):
            key = self.cache_key_func(*args, **kwargs)
            cached_value = self.caching_engine.get_cache_or_none(key)
            if cached_value is None:
                val = function_to_be_decorated(*args, **kwargs)
                if self.should_cache(*args, value_to_cache=val, **kwargs):
                    self.caching_engine.set(key, json.dumps(val))
                return val
            else:
                return cached_value

        return new_func


class AsyncCached:
    """cache a function that returns jsonifiable output"""

    def __init__(self, cache_key_func, caching_engine: CachingEngine, should_cache=None):
        self.cache_key_func = cache_key_func
        self.caching_engine = caching_engine
        self._should_cache = should_cache

    def should_cache(self, *args, **kwargs):
        if self._should_cache is None:
            return True
        else:
            return self._should_cache(*args, **kwargs)

    def __call__(self, function_to_be_decorated):
        async def new_func(*args, **kwargs):
            key = self.cache_key_func(*args, **kwargs)
            cached_value = self.caching_engine.get_cache_or_none(key)
            if cached_value is None:
                val = await function_to_be_decorated(*args, **kwargs)
                if self.should_cache(*args, value_to_cache=val, **kwargs):
                    self.caching_engine.set(key, json.dumps(val))
                return val
            else:
                return cached_value

        return new_func


class RedisCachingEngine(CachingEngine):
    def __init__(self, redis_client, exp):
        self.redis_client = redis_client
        self.exp = exp

    def get_cache_or_none(self, key):
        cache_value = self.redis_client.get(key)
        if cache_value is None:
            return None
        else:
            return json.loads(cache_value)

    def set(self, k, v):
        self.redis_client.set(k, v, ex=self.exp)


class RedisCached(Cached):
    def __init__(self, redis_client, key_func, exp, should_cache=None):
        return super().__init__(key_func, RedisCachingEngine(redis_client, exp), should_cache)


class AsyncRedisCached(AsyncCached):
    def __init__(self, redis_client, key_func, exp, should_cache=None):
        return super().__init__(key_func, RedisCachingEngine(redis_client, exp), should_cache)
