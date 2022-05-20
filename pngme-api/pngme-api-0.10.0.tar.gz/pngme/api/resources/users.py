import asyncio
from abc import ABC
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

from pydantic import validate_arguments

from ..cache import cache
from ..core import BaseClient
from ..encoders import encode_query_params
from ..errors import ServerError
from ..retry import retry_policy

PATH = "/users"

User = Dict[str, Any]


class UsersResponse(TypedDict):
    page: int
    num_pages: int
    users: List[User]


class BaseUsersResource(ABC):
    def __init__(self, client: BaseClient):
        self._client = client

    @retry_policy(
        max_retry_count=4,
        max_retry_interval_seconds=10,
        retryable_exceptions=[ServerError],
    )
    async def _get_page(
        self,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        search: Optional[str] = None,
        page: int = 1,
    ) -> UsersResponse:
        async with self._client.session() as session:
            response = await session.get(
                PATH,
                params=encode_query_params(
                    created_after=created_after,
                    created_before=created_before,
                    search=search,
                    page=page,
                ),
            )

        if response.status_code == 500:
            raise ServerError(response.text)

        assert response.status_code == 200, response.text

        users_response: UsersResponse = response.json()
        return users_response

    @validate_arguments
    @cache
    async def _get(
        self,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> List[User]:
        response = await self._get_page(
            created_after=created_after,
            created_before=created_before,
            search=search,
        )
        max_pages = response["num_pages"]
        if max_pages > 1:
            coroutines = [
                self._get_page(
                    created_after=created_after,
                    created_before=created_before,
                    search=search,
                    page=page + 2,
                )
                for page in range(max_pages - 1)
            ]
            response_pages = await asyncio.gather(*coroutines)
            responses = (response, *response_pages)
        else:
            responses = (response,)

        return [user for response in responses for user in response["users"]]


class AsyncUsersResource(BaseUsersResource):
    async def get(
        self,
        *,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> List[User]:
        return await self._get(
            created_after=created_after,
            created_before=created_before,
            search=search,
        )


class SyncUsersResource(BaseUsersResource):
    def get(
        self,
        *,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> List[User]:
        return self._client.run(
            self._get(
                created_after=created_after,
                created_before=created_before,
                search=search,
            )
        )
