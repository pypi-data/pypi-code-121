import pytest

from tests.sql_models_data import USE_SQLA

pytestmark = pytest.mark.skipif(not USE_SQLA, reason='For SqlAlchemy only')

if USE_SQLA:
    from dropland.storages.containers import SqlStorage, SingleSqlStorage, MultipleSqlStorage, default_sql_storage
    from dropland.storages.sql import SqlStorageType, EngineConfig, SqlStorageEngine
    from tests import MYSQL_URI, POSTGRES_URI, SQLITE_URI


@pytest.mark.asyncio
async def test_create_engine():
    sqlite_config = EngineConfig(
        url=SQLITE_URI,
        pool_min_size=1, pool_max_size=2,
        pool_expire_seconds=15, pool_timeout_seconds=15,
    )
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

    assert engine_factory.create_engine(SqlStorageType.SQLITE, sqlite_config, use_async=False)
    assert engine_factory.create_engine(SqlStorageType.SQLITE, sqlite_config, use_async=True)
    assert engine_factory.create_engine(SqlStorageType.POSTGRES, pg_config, use_async=False)
    assert engine_factory.create_engine(SqlStorageType.POSTGRES, pg_config, use_async=True)
    assert engine_factory.create_engine(SqlStorageType.MYSQL, mysql_config, use_async=False)
    assert engine_factory.create_engine(SqlStorageType.MYSQL, mysql_config, use_async=True)

    for db_type in (SqlStorageType.SQLITE, SqlStorageType.POSTGRES, SqlStorageType.MYSQL):
        for e in engine_factory.get_engines_for_type(db_type, is_async=False):
            assert e.db_type == db_type
            assert e.engine
            assert not e.engine.is_async

        for e in engine_factory.get_engines_for_type(db_type, is_async=True):
            assert e.db_type == db_type
            assert e.engine
            assert e.engine.is_async

    for e in engine_factory.get_engines_for_backend('sqla', is_async=False):
        assert e.backend == 'sqla'
        assert e.engine

    for e in engine_factory.get_engines_for_backend('sqla', is_async=True):
        assert e.backend == 'sqla'
        assert e.engine

    assert engine_factory.get_backend_names() == ['sqla']


@pytest.mark.asyncio
async def test_create_sqlite_engine():
    config = EngineConfig(
        url=SQLITE_URI,
        pool_min_size=1, pool_max_size=2,
        pool_expire_seconds=15, pool_timeout_seconds=15,
    )

    engine = default_sql_storage.create_engine(SqlStorageType.SQLITE, config, use_async=False)
    assert engine
    engine.start()

    with engine.new_connection() as conn:
        res = conn.execute('select sqlite_version();')
        print(res.fetchone()[0])
        res = conn.execute('select 1 + 2;')
        assert res.fetchone()[0] == 3

    engine.stop()

    engine = default_sql_storage.create_engine(SqlStorageType.SQLITE, config, use_async=True)
    assert engine
    await engine.async_start()

    async with engine.new_connection() as conn:
        res = await conn.execute('select sqlite_version();')
        print(res.fetchone()[0])
        res = await conn.execute('select 1 + 2;')
        assert res.fetchone()[0] == 3

    await engine.async_stop()


@pytest.mark.asyncio
async def test_create_pg_engine():
    config = EngineConfig(
        url=POSTGRES_URI,
        pool_min_size=1, pool_max_size=2,
        pool_expire_seconds=15, pool_timeout_seconds=15,
    )

    engine = default_sql_storage.create_engine(SqlStorageType.POSTGRES, config, use_async=False)
    assert engine
    engine.start()

    with engine.new_connection() as conn:
        res = conn.execute('select version();')
        print(res.fetchone()[0])
        res = conn.execute('select 1 + 2;')
        assert res.fetchone()[0] == 3

    engine.stop()

    engine = default_sql_storage.create_engine(SqlStorageType.POSTGRES, config, use_async=True)
    assert engine
    await engine.async_start()

    async with engine.new_connection() as conn:
        res = await conn.execute('select version();')
        print(res.fetchone()[0])
        res = await conn.execute('select 1 + 2;')
        assert res.fetchone()[0] == 3

    await engine.async_stop()


@pytest.mark.asyncio
async def test_create_mysql_engine():
    config = EngineConfig(
        url=MYSQL_URI,
        pool_min_size=1, pool_max_size=2,
        pool_expire_seconds=15, pool_timeout_seconds=15,
    )

    engine = default_sql_storage.create_engine(SqlStorageType.MYSQL, config, use_async=False)
    assert engine
    engine.start()

    with engine.new_connection() as conn:
        res = conn.execute('select version();')
        print(res.fetchone()[0])
        res = conn.execute('select 1 + 2;')
        assert res.fetchone()[0] == 3

    engine.stop()

    engine = default_sql_storage.create_engine(SqlStorageType.MYSQL, config, use_async=True)
    assert engine
    await engine.async_start()

    async with engine.new_connection() as conn:
        res = await conn.execute('select version();')
        print(res.fetchone()[0])
        res = await conn.execute('select 1 + 2;')
        assert res.fetchone()[0] == 3

    await engine.async_stop()


@pytest.mark.asyncio
async def test_storage_container():
    sqlite_config = EngineConfig(
        url=SQLITE_URI,
        pool_min_size=1, pool_max_size=2,
        pool_expire_seconds=15, pool_timeout_seconds=15,
    )

    cont = SqlStorage()

    eng = cont.create_engine(SqlStorageType.SQLITE, sqlite_config, use_async=False)
    assert isinstance(eng, SqlStorageEngine)
    cont.unwire()

    cont = SingleSqlStorage()
    cont.config.from_dict({
        'db_type': SqlStorageType.SQLITE,
        'engine_config': sqlite_config,
        'use_async': False
    })
    eng1 = cont.create_engine()
    eng2 = cont.create_engine()
    assert eng1 is eng2
    cont.unwire()

    cont = MultipleSqlStorage()
    cont.config.from_dict({
        'one': {
            'db_type': SqlStorageType.SQLITE,
            'engine_config': sqlite_config,
            'use_async': False
        },
        'two': {
            'db_type': SqlStorageType.SQLITE,
            'engine_config': sqlite_config,
            'use_async': True
        },
    })

    eng1 = cont.create_engine('one')
    eng2 = cont.create_engine('two')
    assert eng1 is not eng2
    assert eng1.is_async is False
    assert eng2.is_async is True

    cont.unwire()
