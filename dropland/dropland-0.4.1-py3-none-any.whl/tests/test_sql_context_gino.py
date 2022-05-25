import pytest

from tests.sql_models_data import USE_GINO

pytestmark = pytest.mark.skipif(not USE_GINO, reason='For Gino only')

if USE_GINO:
    from dropland.storages.containers import default_sql_storage
    from dropland.storages.sql import SqlStorageType


@pytest.mark.asyncio
async def test_init_context():
    mng = default_sql_storage.manager()

    @mng.use_engines(['gino'])
    async def async_context_func():
        assert not mng.get_connection(SqlStorageType.POSTGRES, 'gino', False)
        assert mng.get_connection(SqlStorageType.POSTGRES, 'gino', True)

        assert 0 == len(mng.get_connections_for_type(SqlStorageType.POSTGRES, False))

        for c in mng.get_connections_for_type(SqlStorageType.POSTGRES, True):
            assert c.engine
            assert c.connection
            assert c.in_transaction

        assert 0 == len(mng.get_connections_for_backend('gino', False))

        for c in mng.get_connections_for_backend('gino', True):
            assert c.engine
            assert c.connection
            assert c.in_transaction

        return mng

    await async_context_func()


@pytest.mark.asyncio
async def test_connections(pg_async_engine, mysql_async_engine):
    mng = default_sql_storage.manager()

    @mng.use_engines(['gino'])
    async def async_context_func():
        created, sql_data = mng.get_or_create_connection(SqlStorageType.POSTGRES, 'gino', False)
        assert not created
        assert not sql_data

        created, sql_data = mng.get_or_create_connection(SqlStorageType.POSTGRES, 'gino', True)
        assert not created
        assert sql_data

        assert sql_data.engine == pg_async_engine

        created, sql_data = mng.get_or_create_connection(SqlStorageType.MYSQL, 'gino', True)
        assert not created
        assert sql_data

        assert sql_data.engine == mysql_async_engine

    await async_context_func()
