__all__ = ('CacheMixin', 'CacheObjectMixin')

import os
from typing import Union

from django.core.cache import cache

from expressmoney.api.utils import log


class BaseCacheMixin:
    _cache_enabled: bool = True
    _cache_period: int = None

    @log
    def flush_cache(self):
        """Delete Redis cache for current endpoint"""
        self._memory_cache = None
        if self._cache_enabled:
            cache.delete(self._get_cache_key())

    @property
    def _cache(self):
        if self._cache_enabled and self._memory_cache is None:
            try:
                total_cache_data = cache.get(self._get_cache_key())
                cache_data = total_cache_data.get(self._data_key) if total_cache_data else None
                self._memory_cache = cache_data
                if os.getenv('IS_ENABLE_API_LOG') and cache_data is not None:
                    print(f'GET REDIS {self}')
            except ModuleNotFoundError:
                cache.set(self._get_cache_key(), None, None)
        return self._memory_cache

    @_cache.setter
    def _cache(self, value):
        if value is not None:
            if self._cache_enabled:
                cache_data = {f'{self._data_key}': value}
                total_cache_data = cache.get(self._get_cache_key())
                if isinstance(total_cache_data, dict):
                    total_cache_data.update(cache_data)
                total_cache_data = total_cache_data if total_cache_data else cache_data
                cache.set(self._get_cache_key(), total_cache_data, self._cache_period)
            self._memory_cache = value

    def _get_related_points(self) -> list:
        """Set related points here"""
        return list()

    def _flush_cache_related_points(self):
        related_points = self._get_related_points()
        for point in related_points:
            point.flush_cache()

    def _get_cache_key(self):
        user_id = getattr(self._user, "id") if self._user is not None else 'none'
        return f'user{user_id}_{self._point_id.id}'

    @property
    def _data_key(self):
        params_key = '_'
        if self._query_params:
            for key, item in self._query_params.items():
                params_key += f'_{key}_{item}'
        if hasattr(self, '_pagination_pages') and self._pagination_pages is not None:
            pagination_key = f'{params_key}_pages{self._pagination_pages}'
        else:
            pagination_key = params_key
        if hasattr(self, '_lookup_field_value'):
            lookup_key = f'{pagination_key}_lookup{self._lookup_field_value}'
        else:
            lookup_key = pagination_key
        return lookup_key


class GetCacheMixin:
    def _get(self, url) -> dict:
        if url is None and self._cache is not None:
            return self._cache
        return super()._get(url=url)


class CacheMixin(GetCacheMixin, BaseCacheMixin):

    def __init__(self,
                 user,
                 query_params: dict = None,
                 is_async: bool = False,
                 timeout: tuple = (30, 30)
                 ):
        super().__init__(user=user,
                         query_params=query_params,
                         is_async=is_async,
                         timeout=timeout,
                         )
        self._memory_cache = None
        self._payload = None

    def _post(self, payload: dict):
        self._payload = payload
        super()._post(payload=payload)
        self._memory_cache = None
        self._flush_cache_related_points()

    def _post_file(self, file, file_name, type_):
        super()._post_file(file=file, file_name=file_name, type_=type_)
        self._memory_cache = None
        self._flush_cache_related_points()


class CacheObjectMixin(GetCacheMixin, BaseCacheMixin):

    def __init__(self,
                 user,
                 lookup_field_value: Union[str, int],
                 is_async: bool = False,
                 timeout: tuple = (30, 30)
                 ):
        super().__init__(user=user,
                         lookup_field_value=lookup_field_value,
                         is_async=is_async,
                         timeout=timeout
                         )
        self._memory_cache = None
        self._payload = None

    def _put(self, payload: dict):
        self._payload = payload
        super()._put(payload=payload)
        self._memory_cache = None
        self._flush_cache_related_points()
