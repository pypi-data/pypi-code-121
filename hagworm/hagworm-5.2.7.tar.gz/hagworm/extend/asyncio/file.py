# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from ..base import Utils
from ..cache import StackCache
from ..error import catch_error

from .net import HTTPClientPool
from .future import ThreadPool


class FileLoader:
    """带缓存的网络文件加载器
    """

    def __init__(self, maxsize=0xff, ttl=3600, thread=32):

        self._cache = StackCache(maxsize, ttl)

        self._thread_pool = ThreadPool(thread)
        self._http_client = HTTPClientPool(limit=thread)

    def _read(self, file):

        with open(file, r'rb') as stream:
            return stream.read()

    async def read(self, file):

        result = None

        with catch_error():

            if self._cache.has(file):

                result = self._cache.get(file)

            else:

                result = await self._thread_pool.run(self._read, file)

                self._cache.set(file, result)

        return result

    async def fetch(self, url, params=None, cookies=None, headers=None):

        result = None

        with catch_error():

            if self._cache.has(url):

                result = self._cache.get(url)

            else:

                result = await self._http_client.get(url, params, cookies, headers)

                self._cache.set(url, result)

        return result
