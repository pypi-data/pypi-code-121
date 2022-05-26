import pytest

from tests.sql_models_data import USE_GINO

pytestmark = pytest.mark.skipif(not USE_GINO, reason='For Gino only')
gino = pytest.importorskip('gino')

if USE_GINO:
    from dropland.storages.containers import default_sql_storage
    from dropland.storages.sql import EngineConfig, SqlStorageType
    from tests import MYSQL_URI, POSTGRES_URI


@pytest.mark.asyncio
async def test_create_engine():
    pg_config = EngineConfig(
        url=POSTGRES_URI,
        pool_min_size=1, pool_max_size=2,
        pool_expire_seconds=15, pool_timeout_seconds=15,
    )
    mysql_config = EngineConfig(
        url=MYSQL_URI,
        pool_min_size=1, pool_max_size=2,
        pool_expire_seconds=15, pool_timeout_seconds=15,
    )

    engine_factory = default_sql_storage.engine_factory()

    assert not engine_factory.create_engine(SqlStorageType.SQLITE, pg_config, use_async=False)
    assert not engine_factory.create_engine(SqlStorageType.SQLITE, pg_config, use_async=True)
    assert not engine_factory.create_engine(SqlStorageType.POSTGRES, pg_config, use_async=False)
    assert engine_factory.create_engine(SqlStorageType.POSTGRES, pg_config, use_async=True)
    assert not engine_factory.create_engine(SqlStorageType.MYSQL, mysql_config, use_async=False)
    assert engine_factory.create_engine(SqlStorageType.MYSQL, mysql_config, use_async=True)

    for db_type in (SqlStorageType.SQLITE, SqlStorageType.POSTGRES, SqlStorageType.MYSQL):
        for e in engine_factory.get_engines_for_type(db_type, is_async=True):
            assert e.db_type == db_type
            assert e.engine
            assert e.engine.is_async

    for e in engine_factory.get_engines_for_backend('gino', is_async=True):
        assert e.backend == 'gino'
        assert e.engine

    assert engine_factory.get_backend_names() == ['gino']


@pytest.mark.asyncio
async def test_create_pg_engine():
    config = EngineConfig(
        url=POSTGRES_URI,
        pool_min_size=1, pool_max_size=2,
        pool_expire_seconds=15, pool_timeout_seconds=15,
    )

    engine = default_sql_storage.create_engine(SqlStorageType.POSTGRES, config, use_async=True)
    assert engine

    with pytest.raises(RuntimeError):
        engine.start()

    await engine.async_start()

    async with engine.new_connection() as conn:
        res = await conn.scalar('select version();')
        print(res)
        res = await conn.scalar('select 1 + 2;')
        assert res == 3

    with pytest.raises(RuntimeError):
        engine.stop()

    await engine.async_stop()

    with pytest.raises(gino.exceptions.UninitializedError):
        assert engine.new_connection()


@pytest.mark.asyncio
async def test_create_mysql_engine():
    config = EngineConfig(
        url=MYSQL_URI,
        pool_min_size=1, pool_max_size=2,
        pool_expire_seconds=15, pool_timeout_seconds=15,
    )

    engine = default_sql_storage.create_engine(SqlStorageType.MYSQL, config, use_async=True)
    assert engine

    with pytest.raises(RuntimeError):
        engine.start()

    await engine.async_start()

    async with engine.new_connection() as conn:
        res = await conn.scalar('select version();')
        print(res)
        res = await conn.scalar('select 1 + 2;')
        assert res == 3

    await engine.async_stop()

    with pytest.raises(gino.exceptions.UninitializedError):
        assert engine.new_connection()
