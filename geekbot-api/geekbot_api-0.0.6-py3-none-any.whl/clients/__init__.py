from abc import ABCMeta
from functools import lru_cache
from typing import Dict
from typing import Optional

import httpx
import requests
from httpx import Response as AsyncResponse
from pydantic import AnyUrl
from requests import Response


class _AbstractClient(metaclass=ABCMeta):
    def __init__(
        self,
        base_api_path: AnyUrl,
        api_version: str,
        path: str,
        api_key: str,
        headers: Optional[Dict] = {},
    ):
        self.api_path = f"{base_api_path}/{api_version}/{path}"
        self.headers = headers
        self.headers["Authorization"] = api_key
        self.headers["user-agent"] = self.headers.get(
            "user-agent", "geekbot-api-pi/0.1.0"
        )

    def _http_get(self, path: str = "") -> Response:
        """Does a get against the geekbot api, adds "path" to the end of self.api_path"""
        r = requests.get(self._get_request_path(path), headers=self.headers)
        return r

    def _http_put(self, data: Dict, path: str = "") -> Response:
        """Does a put against the geekbot api, adds "path" to the end of self.api_path"""
        r = requests.put(self._get_request_path(path), json=data, headers=self.headers)
        return r

    def _http_post(self, data: Dict, path: str = "") -> Response:
        """Does a post against the geekbot api, adds "path" to the end of self.api_path"""
        r = requests.post(self._get_request_path(path), json=data, headers=self.headers)
        return r

    def _http_patch(self, data: Dict, path: str = "") -> Response:
        """Does a post against the geekbot api, adds "path" to the end of self.api_path"""
        r = requests.patch(
            self._get_request_path(path), json=data, headers=self.headers
        )
        return r

    def _http_delete(self, path: str) -> Response:
        """Does a post against the geekbot api, adds "path" to the end of self.api_path"""
        r = requests.delete(self._get_request_path(path), headers=self.headers)
        return r

    @lru_cache(maxsize=None)
    def _get_request_path(self, path: str = "") -> str:
        """combines self.api_path and a path string into a request path"""
        return f"{self.api_path}/{path}" if path != "" else self.api_path

    def __hash__(self):
        return hash(f"{self.api_path}-{type(self).__name__}")


class _AbstractAsyncClient(metaclass=ABCMeta):
    def __init__(
        self,
        base_api_path: AnyUrl,
        api_version: str,
        path: str,
        api_key: str,
        headers: Optional[Dict] = {},
    ):
        self.api_path = f"{base_api_path}/{api_version}/{path}"
        self.headers = headers
        self.headers["Authorization"] = api_key
        self.headers["user-agent"] = self.headers.get(
            "user-agent", "geekbot-api-pi/0.1.0"
        )

    async def _http_get(self, path: str = "") -> AsyncResponse:
        """Does a get against the geekbot api, adds "path" to the end of self.api_path"""
        async with httpx.AsyncClient() as client:
            r = await client.get(self._get_request_path(path), headers=self.headers)
        return r

    async def _http_put(self, data: Dict, path: str = "") -> AsyncResponse:
        """Does a put against the geekbot api, adds "path" to the end of self.api_path"""
        async with httpx.AsyncClient() as client:
            r = await client.put(
                self._get_request_path(path), json=data, headers=self.headers
            )
        return r

    async def _http_post(self, data: Dict, path: str = "") -> AsyncResponse:
        """Does a post against the geekbot api, adds "path" to the end of self.api_path"""
        async with httpx.AsyncClient() as client:
            r = await client.post(
                self._get_request_path(path), json=data, headers=self.headers
            )
        return r

    async def _http_patch(self, data: Dict, path: str = "") -> AsyncResponse:
        """Does a post against the geekbot api, adds "path" to the end of self.api_path"""
        async with httpx.AsyncClient() as client:
            r = await client.patch(
                self._get_request_path(path), json=data, headers=self.headers
            )
        return r

    async def _http_delete(self, path: str) -> AsyncResponse:
        """Does a post against the geekbot api, adds "path" to the end of self.api_path"""
        async with httpx.AsyncClient() as client:
            r = await client.delete(self._get_request_path(path), headers=self.headers)
        return r

    @lru_cache(maxsize=None)
    def _get_request_path(self, path: str = "") -> str:
        """combines self.api_path and a path string into a request path"""
        return f"{self.api_path}/{path}" if path != "" else self.api_path

    def __hash__(self):
        return hash(f"{self.api_path}-{type(self).__name__}")
