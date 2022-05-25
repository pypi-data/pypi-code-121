import pytest

from dropland.storages.redis import USE_REDIS

pytestmark = pytest.mark.skipif(not USE_REDIS, reason='For Redis only')

if USE_REDIS:
    from dropland.storages.containers import RedisStorage, SingleRedisStorage, MultipleRedisStorage, \
        default_redis_storage
    from dropland.storages.redis import EngineConfig, RedisStorageEngine
    from tests import REDIS_URI


@pytest.mark.asyncio
async def test_create_engine():
    engine_factory = default_redis_storage.engine_factory()

    assert not engine_factory.get_engine('')

    config = EngineConfig(url=REDIS_URI)
    assert engine_factory.create_engine('dropland', config)

    engine = engine_factory.get_engine('dropland')
    assert engine
    assert engine.backend is engine_factory
    assert engine.is_async

    assert engine_factory.get_engine_names() == ['dropland']


@pytest.mark.asyncio
async def test_create_connection():
    engine_factory = default_redis_storage.engine_factory()

    config = EngineConfig(url=REDIS_URI)
    engine = engine_factory.create_engine('dropland', config)

    assert engine
    await engine.async_start()

    async with engine.new_connection() as conn:
        assert await conn.set('kkk', 'vvv') is True
        assert b'vvv' == await conn.get('kkk')
        assert await conn.delete('kkk')

    await engine.async_stop()


@pytest.mark.asyncio
async def test_storage_container():
    config = EngineConfig(url=REDIS_URI)

    cont = RedisStorage()

    eng = cont.create_engine('dropland', config)
    assert isinstance(eng, RedisStorageEngine)
    assert eng.name == 'dropland'
    cont.unwire()

    cont = SingleRedisStorage()
    cont.config.from_dict({
        'name': 'dropland1',
        'engine_config': config
    })
    eng1 = cont.create_engine()
    eng2 = cont.create_engine()
    assert eng1 is eng2
    cont.unwire()

    cont = MultipleRedisStorage()
    cont.config.from_dict({
        'one': {
            'name': 'dropland1',
            'engine_config': config
        },
        'two': {
            'name': 'dropland2',
            'engine_config': config
        },
    })

    eng1 = cont.create_engine('one')
    eng2 = cont.create_engine('two')
    assert eng1 is not eng2
    assert eng1.is_async is True
    assert eng2.is_async is True
    assert eng1.name == 'dropland1'
    assert eng2.name == 'dropland2'

    cont.unwire()
