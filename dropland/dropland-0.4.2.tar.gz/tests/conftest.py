import asyncio

import pytest

from dropland.storages.redis import USE_REDIS
from dropland.storages.sql import USE_SQL

if USE_REDIS:
    from dropland.storages.containers import default_redis_storage
    from dropland.storages.redis import EngineConfig as RedisEngineConfig

if USE_SQL:
    from dropland.storages.containers import MultipleSqlStorage
    from dropland.storages.sql import EngineConfig as SqlEngineConfig, SqlStorageType

from tests import MYSQL_URI, POSTGRES_URI, REDIS_URI, SQLITE_URI


if USE_SQL:
    sql_storage = MultipleSqlStorage()

    sql_storage.config.from_dict({
        'sqlite': {
            'db_type': SqlStorageType.SQLITE,
            'engine_config': SqlEngineConfig(
                url=SQLITE_URI,
                pool_min_size=1, pool_max_size=2,
                pool_expire_seconds=15, pool_timeout_seconds=15,
            ),
            'use_async': False
        },
        'asqlite': {
            'db_type': SqlStorageType.SQLITE,
            'engine_config': SqlEngineConfig(
                url=SQLITE_URI,
                pool_min_size=1, pool_max_size=2,
                pool_expire_seconds=15, pool_timeout_seconds=15,
            ),
            'use_async': True
        },
        'pg': {
            'db_type': SqlStorageType.POSTGRES,
            'engine_config': SqlEngineConfig(
                url=POSTGRES_URI,
                pool_min_size=1, pool_max_size=2,
                pool_expire_seconds=15, pool_timeout_seconds=15,
            ),
            'use_async': False
        },
        'apg': {
            'db_type': SqlStorageType.POSTGRES,
            'engine_config': SqlEngineConfig(
                url=POSTGRES_URI,
                pool_min_size=1, pool_max_size=2,
                pool_expire_seconds=15, pool_timeout_seconds=15,
            ),
            'use_async': True
        },
        'apg-gino': {
            'db_type': SqlStorageType.POSTGRES,
            'engine_config': SqlEngineConfig(
                url=POSTGRES_URI,
                pool_min_size=1, pool_max_size=2,
                pool_expire_seconds=15, pool_timeout_seconds=15,
            ),
            'use_async': True,
            'backend_name': 'gino'
        },
        'ms': {
            'db_type': SqlStorageType.MYSQL,
            'engine_config': SqlEngineConfig(
                url=MYSQL_URI,
                pool_min_size=1, pool_max_size=2,
                pool_expire_seconds=15, pool_timeout_seconds=15,
            ),
            'use_async': False
        },
        'ams': {
            'db_type': SqlStorageType.MYSQL,
            'engine_config': SqlEngineConfig(
                url=MYSQL_URI,
                pool_min_size=1, pool_max_size=2,
                pool_expire_seconds=15, pool_timeout_seconds=15,
            ),
            'use_async': True
        },
        'ams-gino': {
            'db_type': SqlStorageType.MYSQL,
            'engine_config': SqlEngineConfig(
                url=MYSQL_URI,
                pool_min_size=1, pool_max_size=2,
                pool_expire_seconds=15, pool_timeout_seconds=15,
            ),
            'use_async': True,
            'backend_name': 'gino'
        },
    })


@pytest.fixture(scope='session')
def test_sql_storage():
    return sql_storage


@pytest.fixture(scope='session')
def test_redis_storage():
    if USE_REDIS:
        return default_redis_storage
    else:
        return None


@pytest.fixture(scope='session')
def sqlite_engine(test_sql_storage):
    return test_sql_storage.create_engine('sqlite')


@pytest.fixture(scope='session')
def sqlite_async_engine(test_sql_storage):
    return test_sql_storage.create_engine('asqlite')


@pytest.fixture(scope='session')
def pg_engine(test_sql_storage):
    return test_sql_storage.create_engine('pg')


@pytest.fixture(scope='session')
def pg_async_engine(test_sql_storage):
    return test_sql_storage.create_engine('apg')


@pytest.fixture(scope='session')
def mysql_engine(test_sql_storage):
    return test_sql_storage.create_engine('ms')


@pytest.fixture(scope='session')
def mysql_async_engine(test_sql_storage):
    return test_sql_storage.create_engine('ams')


@pytest.fixture(scope='session')
def pg_gino_engine(test_sql_storage):
    return test_sql_storage.create_engine('apg-gino')


@pytest.fixture(scope='session')
def mysql_gino_engine(test_sql_storage):
    return test_sql_storage.create_engine('ams-gino')


@pytest.fixture(scope='session')
def redis_engine(test_redis_storage):
    engine_config = RedisEngineConfig(url=REDIS_URI)
    return test_redis_storage.create_engine('dropland', engine_config)


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


if USE_SQL:
    @pytest.fixture(scope='function')
    async def _sql_ctx(event_loop, test_sql_storage):
        if USE_SQL:
            async with test_sql_storage.manager().with_async_engines(autocommit=False) as ctx:
                yield ctx
        else:
            yield


    @pytest.fixture(scope='function')
    def sql_ctx(_sql_ctx, test_sql_storage):
        with test_sql_storage.manager().set_context(_sql_ctx):
            yield _sql_ctx


if USE_REDIS:
    @pytest.fixture(scope='function')
    async def _redis_ctx(event_loop, test_redis_storage):
        if USE_REDIS:
            async with test_redis_storage.manager().with_async_engines() as ctx:
                yield ctx
        else:
            yield


    @pytest.fixture(scope='function')
    def redis_ctx(_redis_ctx, test_redis_storage):
        with test_redis_storage.manager().set_context(_redis_ctx):
            yield _redis_ctx


    @pytest.fixture(scope='function')
    async def data_ctx(sql_ctx, redis_ctx):
        yield sql_ctx, redis_ctx


if USE_SQL:
    @pytest.fixture(scope='function')
    async def data_ctx(sql_ctx):
        yield sql_ctx, None

elif USE_REDIS:
    @pytest.fixture(scope='function')
    async def data_ctx(redis_ctx):
        yield None, redis_ctx
