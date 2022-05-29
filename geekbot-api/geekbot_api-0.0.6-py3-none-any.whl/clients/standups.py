from typing import List
from typing import Optional

from . import _AbstractAsyncClient
from . import _AbstractClient
from ..schemas import Standup
from ..schemas import StandupDuplicateIn
from ..schemas import StandupIn


class _StandupsClient(_AbstractClient):
    def list(self):
        """gets Standups and yields them as a generator"""
        response = self._http_get()
        response_json = response.json()
        if isinstance(response_json, list):
            if len(response_json) == 0:
                return
            else:
                for standup in response.json():
                    yield Standup(**standup)
        else:
            yield Standup(**response_json)

    def get(self, standup_id: str) -> Optional[Standup]:
        """gets a standup by id"""
        response = self._http_get(path=standup_id)
        if response.status_code == 404:
            return None
        return Standup(**response.json())

    def create(self, standup_in: StandupIn) -> Standup:
        """Create a standup"""
        response = self._http_post(data=standup_in.dict())
        return Standup(**response.json())

    def update(self, standup_id: str, standup_in: StandupDuplicateIn) -> Standup:
        """Update a standup"""
        response = self._http_patch(data=standup_id.dict())
        return Standup(**response.json())

    def duplicate(self, standup_id: str, standup_in: StandupDuplicateIn) -> Standup:
        """Duplicate a standup"""
        response = self._http_post(
            path=f"{standup_id}/duplicate", data=standup_in.dict()
        )
        return Standup(**response.json())

    def delete(self, standup_id: str) -> bool:
        """Delete a standup"""
        response = self._http_delete(path=standup_id)
        return response.status_code == 200

    def start(
        self,
        standup_id: str,
        user_ids: Optional[List[int]],
        emails: Optional[List[str]],
    ) -> bool:
        """Start a standup immediately"""
        response = self._http_post(
            path=f"{standup_id}/start", data={"users": user_ids, "emails": emails}
        )
        return response.status_code == 200


class _StandupsAsyncClient(_AbstractAsyncClient):
    async def list(self):
        """gets Standups and yields them as a generator"""
        response = await self._http_get()
        response_json = response.json()
        if isinstance(response_json, list):
            if len(response_json) == 0:
                return
            else:
                for standup in response.json():
                    yield Standup(**standup)
        else:
            yield Standup(**response_json)

    async def get(self, standup_id: str) -> Optional[Standup]:
        """gets a standup by id"""
        response = await self._http_get(path=standup_id)
        if response.status_code == 404:
            return None
        return Standup(**response.json())

    async def create(self, standup_in: StandupIn) -> Standup:
        """Create a standup"""
        response = await self._http_post(data=standup_in.dict())
        return Standup(**response.json())

    async def update(self, standup_id: str, standup_in: StandupDuplicateIn) -> Standup:
        """Update a standup"""
        response = await self._http_patch(data=standup_id.dict())
        return Standup(**response.json())

    async def duplicate(
        self, standup_id: str, standup_in: StandupDuplicateIn
    ) -> Standup:
        """Duplicate a standup"""
        response = await self._http_post(
            path=f"{standup_id}/duplicate", data=standup_in.dict()
        )
        return Standup(**response.json())

    async def delete(self, standup_id: str) -> bool:
        """Delete a standup"""
        response = await self._http_delete(path=standup_id)
        return response.status_code == 200

    async def start(
        self,
        standup_id: str,
        user_ids: Optional[List[int]],
        emails: Optional[List[str]],
    ) -> bool:
        response = await self._http_post(
            path=f"{standup_id}/start", data={"users": user_ids, "emails": emails}
        )
        return response.status_code == 200
