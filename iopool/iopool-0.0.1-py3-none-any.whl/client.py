from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx


from .const import ROUTES
from .errors import WrongApiKeyError
from .meta import __version__

if TYPE_CHECKING:
    from typing import Any

    from .types import Pool


__all__ = ["Client", "AsyncClient"]


@dataclass
class BaseClient:
    """Common base for all IOPool API clients"""

    api_key: str
    """A valid API Key to authenticate against API"""

    @property
    def headers(self) -> dict:
        """Returns a dictionary of headers to be used with requests"""
        return {
            "x-api-key": self.api_key,
            "user-agent": f"iopool-python-client/{__version__}",
        }

    def handle_response(self, response: httpx.Response) -> Any:
        """Handles the response from the API, raises exceptions if necessary"""
        try:
            response.raise_for_status()
        except httpx.HTTPError as e:
            if e.response.status_code == 403:
                raise WrongApiKeyError
            raise
        return response.json()


class Client(BaseClient):
    """An IOPool API client"""

    def pools(self) -> list[Pool]:
        """Returns a list of all pools"""
        response = httpx.get(ROUTES.url_for("pools"), headers=self.headers)
        return self.handle_response(response)

    def pool(self, pool_id: str) -> Pool:
        """Returns a single pool"""
        response = httpx.get(ROUTES.url_for("pool", pool_id=pool_id), headers=self.headers)
        return self.handle_response(response)


class AsyncClient(BaseClient):
    """An IOPool async API client"""

    async def pools(self) -> list[Pool]:
        """Returns a list of all pools"""
        async with httpx.AsyncClient() as client:
            response = await client.get(ROUTES.url_for("pools"), headers=self.headers)
        return self.handle_response(response)

    async def pool(self, pool_id: str) -> Pool:
        """Returns a single pool"""
        async with httpx.AsyncClient() as client:
            response = await client.get(ROUTES.url_for("pool", pool_id=pool_id), headers=self.headers)
        return self.handle_response(response)
