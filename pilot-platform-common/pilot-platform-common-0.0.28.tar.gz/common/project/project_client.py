# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import json

import aioredis
import httpx

from .project_exceptions import ProjectException, ProjectNotFoundException

CACHE_PREFIX = "project_client-"
CACHE_EXPIRY = 300


class ProjectObject(object):
    attributes = [
        "id",
        "code",
        "name",
        "description",
        "image_url",
        "tags",
        "system_tags",
        "is_discoverable",
        "created_at",
        "updated_at",
    ]

    def __init__(self, data, project_client):
        self.project_client = project_client
        for attr in self.attributes:
            setattr(self, attr, data.get(attr))

    def __repr__(self):
        return f"<Project {self.code}>"

    async def json(self):
        result = {}
        for attr in self.attributes:
            result[attr] = getattr(self, attr, "")
        return result

    async def update(
        self,
        code=None,
        name=None,
        description=None,
        image_url=None,
        tags=None,
        system_tags=None,
        is_discoverable=None
    ):
        await self.project_client.connect_redis()
        data = {
            "code": code,
            "name": name,
            "description": description,
            "image_url": image_url,
            "tags": tags,
            "system_tags": system_tags,
            "is_discoverable": is_discoverable,
        }
        # remove blank items
        data = {k: v for k, v in data.items() if v is not None}

        async with httpx.AsyncClient() as client:
            response = await client.patch(self.project_client.base_url + f"/v1/projects/{self.id}", json=data)
        if response.status_code == 404:
            raise ProjectNotFoundException
        elif response.status_code != 200:
            raise ProjectException(status_code=response.status_code, error_msg=response.json())

        await self.project_client.redis.delete(CACHE_PREFIX + self.id)
        await self.project_client.redis.delete(CACHE_PREFIX + self.code)
        for attr in self.attributes:
            setattr(self, attr, response.json().get(attr))
        return self

    async def upload_logo(self, image_data):
        data = {
            "base64": image_data
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.project_client.base_url + f"/v1/projects/{self.id}/logo", json=data)
        if response.status_code == 404:
            raise ProjectNotFoundException
        elif response.status_code != 200:
            raise ProjectException(status_code=response.status_code, error_msg=response.json())
        return self


class ProjectClient(object):
    def __init__(self, project_url, redis_url, enable_cache=True, is_async=True):
        self.base_url = project_url
        self.enable_cache = enable_cache
        self.redis_url = redis_url
        if is_async:
            self.project_object = ProjectObject
        else:
            self.project_object = ProjectObjectSync

    async def connect_redis(self):
        self.redis = await aioredis.from_url(self.redis_url)

    async def search(
        self,
        page=None,
        page_size=None,
        order_by=None,
        order_type=None,
        name=None,
        code=None,
        description=None,
        is_discoverable=None,
        tags_all=None,
        code_any=None,
        created_at_start=None,
        created_at_end=None,
    ):
        data = {
            "page": page,
            "page_size": page_size,
            "sort_by": order_by,
            "sort_order": order_type,
            "name": name,
            "code": code,
            "description": description,
            "is_discoverable": is_discoverable,
            "tags_all": tags_all,
            "code_any": code_any,
            "created_at_start": created_at_start,
            "created_at_end": created_at_end,
        }
        # remove blank items
        data = {k: v for k, v in data.items() if v is not None}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url + "/v1/projects/", params=data)
        if response.status_code == 404:
            raise ProjectNotFoundException
        elif response.status_code != 200:
            raise ProjectException(status_code=response.status_code, error_msg=response.json())
        result = response.json()
        result["result"] = [self.project_object(item, self) for item in response.json()["result"]]
        return result

    async def get(self, id="", code=""):
        await self.connect_redis()
        project_id = ""
        if id:
            project_id = id
        else:
            project_id = code

        project_key = CACHE_PREFIX + project_id
        if self.enable_cache and await self.redis.exists(project_key):
            return self.project_object(json.loads(await self.redis.get(project_key)), self)

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url + f"/v1/projects/{project_id}")
        if response.status_code == 404:
            raise ProjectNotFoundException
        elif response.status_code != 200:
            raise ProjectException(status_code=response.status_code, error_msg=response.json())

        if self.enable_cache:
            await self.redis.setex(project_key, CACHE_EXPIRY, json.dumps(response.json()))
        return self.project_object(response.json(), self)

    async def create(self, code, name, description, image_url=None, tags=[], system_tags=[], is_discoverable=True):
        data = {
            "code": code,
            "name": name,
            "description": description,
            "image_url": image_url,
            "tags": tags,
            "system_tags": system_tags,
            "is_discoverable": is_discoverable,
        }
        # remove blank items
        data = {k: v for k, v in data.items() if v is not None}

        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url + "/v1/projects/", json=data)
        if response.status_code != 200:
            raise ProjectException(status_code=response.status_code, error_msg=response.json())
        return self.project_object(response.json(), self)


class ProjectObjectSync(ProjectObject):
    def __init__(self, *args, **kwargs):
        self.project_object = ProjectObject(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def json(self, *args, **kwargs):
        return asyncio.run(self.project_object.json(*args, **kwargs))

    def update(self, *args, **kwargs):
        asyncio.run(self.project_object.update(*args, **kwargs))
        for attr in self.attributes:
            setattr(self, attr, getattr(self.project_object, attr))
        return self

    def upload_logo(self, *args, **kwargs):
        asyncio.run(self.project_object.upload_logo(*args, **kwargs))
        for attr in self.attributes:
            setattr(self, attr, getattr(self.project_object, attr))
        return self


class ProjectClientSync(object):
    def __init__(self, project_url, redis_url, enable_cache=True):
        self.project_client = ProjectClient(project_url, redis_url, enable_cache=enable_cache, is_async=False)
        asyncio.run(self.project_client.connect_redis())

    def get(self, *args, **kwargs):
        return asyncio.run(self.project_client.get(*args, **kwargs))

    def search(self, *args, **kwargs):
        return asyncio.run(self.project_client.search(*args, **kwargs))

    def create(self, *args, **kwargs):
        return asyncio.run(self.project_client.create(*args, **kwargs))
