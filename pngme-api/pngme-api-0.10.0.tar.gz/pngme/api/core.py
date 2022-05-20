import asyncio
import json
import time
from abc import ABC
from base64 import b64decode
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Awaitable, Dict, TypeVar

import httpx
import nest_asyncio

nest_asyncio.apply()


T = TypeVar("T")


class AccessTokenInvalid(Exception):
    """Raised when access token does not match the expected format."""


class AccessTokenExpired(Exception):
    """Raised when access token has already expired."""


def _decode_jwt_payload(access_token: str) -> Dict[str, Any]:
    """Extract the JWT payload without performing signature validation."""
    try:
        parts = access_token.split(".")
        _, payload_b64, _ = parts
        # Append padding to base64 string to ensure it can be decoded. Since
        # padding in base64 is optional, Cognito does not add padding to ID
        # tokens which causes base64.b64decode to raise binascii.Error. Adding
        # padding to the end ensures that JWTs can be decoded successfully and
        # won't break JWTs which already contain padding.
        payload_bytes = b64decode(payload_b64 + "==")
        payload: Dict[str, Any] = json.loads(payload_bytes)
        return payload
    except:
        raise AccessTokenInvalid


def _validate_access_token(access_token: str) -> str:
    """Return the access token if valid or raise a related exception."""
    payload = _decode_jwt_payload(access_token)

    expires_at = payload.get("exp", 0)
    if expires_at < time.time():
        raise AccessTokenExpired

    return access_token


class BaseClient(ABC):
    def __init__(
        self,
        access_token: str,
        concurrency_limit: int = 50,
        base_url: str = "https://api.pngme.com/beta",
    ):
        """Client SDK to interact with Pngme financial report resources.

        Args:
            access_token: API key from https://admin.pngme.com
            concurrency_limit: maximum allowed concurrent API requests
            base_url: root url for API resources
        """
        self.access_token = _validate_access_token(access_token)
        self.base_url = base_url

        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    def run(self, coroutine: Awaitable[T]) -> T:
        """Run coroutine in managed event loop."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        return loop.run_until_complete(coroutine)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Configure connection and concurrency settings."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        transport = httpx.AsyncHTTPTransport(retries=10)

        async with self.semaphore:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30,
                transport=transport,
            ) as session:
                yield session
