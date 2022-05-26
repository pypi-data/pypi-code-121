import asyncio

import aioredis


class RedisClient:
    def __init__(self, uri):
        self.r = aioredis.from_url(uri)

    async def get(self, key):
        return await self.r.get(key)

    async def set(self, key, value, ex=None):
        return await self.r.set(key, value, ex=ex)
