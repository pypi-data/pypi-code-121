import json

from ekp_sdk.services.redis_client import RedisClient


class CacheService:
    def __init__(
        self,
        redis_client: RedisClient
    ):
        self.redis_client = redis_client

    async def get(self, key):
        value = await self.redis_client.get(key)
        if (value is None):
            return None
        return json.loads(value)

    async def set(self, key, value, ex=None):
        if (value is not None):
            return await self.redis_client.set(key, json.dumps(value), ex=ex)

        return await self.redis_client.set(key, value)

    async def wrap(self, key, fn, ex=None):

        cache_value = await self.get(key)

        if (cache_value is not None):
            return cache_value

        value = await fn()

        await self.set(key, value)

        return value
