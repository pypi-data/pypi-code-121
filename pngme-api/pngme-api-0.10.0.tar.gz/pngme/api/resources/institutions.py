from abc import ABC
from typing import Any, Dict, List, TypedDict

from pydantic import validate_arguments

from ..cache import cache
from ..core import BaseClient

PATH = "/users/{user_uuid}/institutions"

Institution = Dict[str, Any]


class InstitutionsResponse(TypedDict):
    institutions: List[Institution]


class BaseInstitutionsResource(ABC):
    def __init__(self, client: BaseClient):
        self._client = client

    @validate_arguments
    @cache
    async def _get(self, user_uuid: str) -> List[Institution]:
        async with self._client.session() as session:
            response = await session.get(PATH.format(user_uuid=user_uuid))

        assert response.status_code == 200, response.text

        institutions_response: InstitutionsResponse = response.json()
        return institutions_response["institutions"]


class AsyncInstitutionsResource(BaseInstitutionsResource):
    async def get(self, user_uuid: str) -> List[Institution]:
        return await self._get(user_uuid)


class SyncInstitutionsResource(BaseInstitutionsResource):
    def get(self, user_uuid: str) -> List[Institution]:
        return self._client.run(self._get(user_uuid))
