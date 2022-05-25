import pytest

from dropland.storages.redis import USE_REDIS

pytestmark = pytest.mark.skipif(not USE_REDIS, reason='For Redis only')


@pytest.mark.asyncio
async def test_init_context(test_redis_storage, redis_engine):
    mng = test_redis_storage.manager()

    @mng.use_engines(['dropland'])
    async def context_func():
        assert not mng.get_connection('_')

        redis_data = mng.get_connection('dropland')
        assert redis_data
        assert redis_data.engine
        assert redis_data.connection

    await context_func()


@pytest.mark.asyncio
async def test_connections(test_redis_storage, redis_engine):
    mng = test_redis_storage.manager()

    @mng.use_engines(['dropland'])
    async def context_func():
        created, redis_data = mng.get_or_create_connection('dropland')
        assert not created
        assert redis_data

        assert redis_data.engine == redis_engine
        assert redis_data.connection

    await context_func()
