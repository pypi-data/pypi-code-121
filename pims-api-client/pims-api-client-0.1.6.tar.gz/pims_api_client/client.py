from .configurator import Configurator
from .exceptions import raise_the_desired_api_error, method_catches_httpx_request_error
import json
from typing import Any

import httpx
from humps.main import decamelize, camelize
from urllib.parse import urljoin


class BaseApiClient:

    def __init__(self, configurator: Configurator):
        self.configurator = configurator

    @property
    def _headers(self):
        return {
            "Authorization": 'Bearer {}'.format(self.configurator.bearer_token),
            "Content-Type": 'application/json',
            "Accept": 'application/json'
        }

    @method_catches_httpx_request_error
    async def post(self, path:str, data={}, timeout=20, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                urljoin(self.configurator.base_url, path),
                headers=self._headers,
                data=json.dumps(self._prepare_data(data)),
                timeout=timeout
            )
        return self._process_response(response)

    @method_catches_httpx_request_error
    async def get(self, path:str, params={}, timeout=20, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                urljoin(self.configurator.base_url, path),
                headers=self._headers,
                params=self._prepare_data(params),
                timeout=timeout
            )

        return self._process_response(response)

    def _prepare_data(self, data: dict) -> dict:
        cache = {k: v for k, v in data.items() if v}
        return camelize(cache)

    def _process_response(self, response: Any) -> dict:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise_the_desired_api_error(exc)
        return decamelize(response.json())