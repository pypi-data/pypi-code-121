import asyncio
import aioredis
import platform
from sometools.async_tools.base import Base

if not (platform.system() == 'Windows'):
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # 使用 uvloop 来替换 asyncio 内部的事件循环。


class AsyncIoRedisMixIn(Base):
    def __init__(self, *args, **kwargs):
        super(AsyncIoRedisMixIn, self).__init__(*args, **kwargs)

    async def get_async_redis_conn(self, **kwargs):
        # Redis client bound to pool of connections (auto-reconnecting).
        # https://aioredis.readthedocs.io/en/latest/
        return aioredis.from_url(
            f"redis://:{kwargs.get('redis_pwd')}@{kwargs.get('redis_host')}:{kwargs.get('redis_port')}/{kwargs.get('redis_db')}", encoding="utf-8", decode_responses=True
        )


    async def aio_redis_conn_close(self):
        if self.aio_redis_conn:
            self.aio_redis_conn.close()
            await self.aio_redis_conn.wait_closed()

# async def test():
#     redis = GeneralAsyncIoRedis()
#     r = await redis.get_redis_pool()
#     await redis.set('my-key', 'value')
#     value = await redis.get('my-key', encoding='utf-8')
#     await redis.close()
