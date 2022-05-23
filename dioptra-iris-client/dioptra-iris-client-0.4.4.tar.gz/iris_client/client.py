import json
import os
from typing import Any, AsyncIterator, Iterator, List, Optional, Tuple

from authlib.integrations.httpx_client import AsyncOAuth2Client, OAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token

from iris_client.constants import (
    BASE_URL_ENV,
    CREDENTIALS_FILE,
    LOGIN_URL,
    PAGINATION_DATA_KEY,
    PAGINATION_NEXT_KEY,
    PASSWORD_ENV,
    USERNAME_ENV,
)
from iris_client.logger import logger


def get_credentials(
    base_url: Optional[str],
    username: Optional[str],
    password: Optional[str],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if username or password:
        logger.debug("using credentials from arguments")
        return base_url, username, password
    if (
        BASE_URL_ENV in os.environ
        or USERNAME_ENV in os.environ
        or PASSWORD_ENV in os.environ
    ):
        logger.debug("using credentials from environment")
        return (
            os.environ.get(BASE_URL_ENV),
            os.environ.get(USERNAME_ENV),
            os.environ.get(PASSWORD_ENV),
        )
    if CREDENTIALS_FILE.exists():
        logger.debug("using credentials from %s", CREDENTIALS_FILE)
        credentials = json.loads(CREDENTIALS_FILE.read_text())
        return (
            credentials.get("base_url"),
            credentials.get("username"),
            credentials.get("password"),
        )
    return None, None, None


class IrisClient(OAuth2Client):
    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        fetch_token: bool = True,
        follow_redirects: bool = True,
        **kwargs: Any,
    ) -> None:
        self.base_url, self.username, self.password = get_credentials(
            base_url, username, password
        )
        self.fetch_token_ = fetch_token
        super().__init__(
            base_url=self.base_url, follow_redirects=follow_redirects, **kwargs
        )

    def __enter__(self) -> "IrisClient":
        super().__enter__()
        if self.fetch_token_:
            self.fetch_token()
        return self

    def fetch_token(self, **kwargs: Any) -> OAuth2Token:
        return super().fetch_token(
            LOGIN_URL, username=self.username, password=self.password
        )

    def all(self, url: str, **kwargs: Any) -> List[dict]:
        return list(self.all_iter(url, **kwargs))

    def all_iter(self, url: str, **kwargs: Any) -> Iterator[dict]:
        while url:
            data = self.get(url, **kwargs).json()
            url = data[PAGINATION_NEXT_KEY]
            yield from data[PAGINATION_DATA_KEY]


class AsyncIrisClient(AsyncOAuth2Client):
    def __init__(
        self,
        base_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        fetch_token: bool = True,
        follow_redirects: bool = True,
        **kwargs: Any,
    ) -> None:
        self.base_url, self.username, self.password = get_credentials(
            base_url, username, password
        )
        self.fetch_token_ = fetch_token
        super().__init__(
            base_url=self.base_url, follow_redirects=follow_redirects, **kwargs
        )

    async def __aenter__(self) -> "AsyncIrisClient":
        await super().__aenter__()
        if self.fetch_token_:
            await self.fetch_token()
        return self

    async def fetch_token(self, **kwargs: Any) -> OAuth2Token:
        return await super().fetch_token(
            LOGIN_URL, username=self.username, password=self.password
        )

    async def all(self, url: str, **kwargs: Any) -> List[dict]:
        return [x async for x in self.all_iter(url, **kwargs)]

    async def all_iter(self, url: str, **kwargs: Any) -> AsyncIterator[dict]:
        while url:
            data = (await self.get(url, **kwargs)).json()
            url = data[PAGINATION_NEXT_KEY]
            for obj in data[PAGINATION_DATA_KEY]:
                yield obj
