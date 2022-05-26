import pytest

from tests.sql_models_data import USE_SQLA

pytestmark = pytest.mark.skipif(not USE_SQLA, reason='For SqlAlchemy only')

if USE_SQLA:
    from dropland.storages.sql import SqlStorageType


@pytest.mark.asyncio
async def test_init_context(test_sql_storage, sqlite_engine, sqlite_async_engine):
    mng = test_sql_storage.manager()

    @mng.use_engines(['sqla'])
    def sync_context_func():
        assert mng.get_connection(SqlStorageType.SQLITE, 'sqla', False)
        assert not mng.get_connection(SqlStorageType.SQLITE, 'sqla', True)

        for c in mng.get_connections_for_type(SqlStorageType.SQLITE, False):
            assert c.engine
            assert c.connection
            assert c.in_transaction

        assert 0 == len(mng.get_connections_for_type(SqlStorageType.SQLITE, True))

        for c in mng.get_connections_for_backend('sqla', False):
            assert c.engine
            assert c.connection
            assert c.in_transaction

        assert 0 == len(mng.get_connections_for_backend('sqla', True))

    @mng.use_engines(['sqla'])
    async def async_context_func():
        assert not mng.get_connection(SqlStorageType.SQLITE, 'sqla', False)
        assert mng.get_connection(SqlStorageType.SQLITE, 'sqla', True)

        assert 0 == len(mng.get_connections_for_type(SqlStorageType.SQLITE, False))

        for c in mng.get_connections_for_type(SqlStorageType.SQLITE, True):
            assert c.engine
            assert c.connection
            assert c.in_transaction

        assert 0 == len(mng.get_connections_for_backend('sqla', False))

        for c in mng.get_connections_for_backend('sqla', True):
            assert c.engine
            assert c.connection
            assert c.in_transaction

    sync_context_func()
    await async_context_func()


@pytest.mark.asyncio
async def test_connections(test_sql_storage, sqlite_engine, sqlite_async_engine):
    mng = test_sql_storage.manager()

    @mng.use_engines(['sqla'])
    def sync_context_func():
        created, sql_data = mng.get_or_create_connection(SqlStorageType.SQLITE, 'sqla', False)
        assert not created
        assert sql_data

        assert sql_data.engine == sqlite_engine

        created, sql_data = mng.get_or_create_connection(SqlStorageType.SQLITE, 'sqla', True)
        assert created
        assert sql_data

        assert sql_data.engine == sqlite_async_engine

    @mng.use_engines(['sqla'])
    async def async_context_func():
        created, sql_data = mng.get_or_create_connection(SqlStorageType.SQLITE, 'sqla', False)
        assert created
        assert sql_data

        assert sql_data.engine == sqlite_engine

        created, sql_data = mng.get_or_create_connection(SqlStorageType.SQLITE, 'sqla', True)
        assert not created
        assert sql_data

        assert sql_data.engine == sqlite_async_engine

    sync_context_func()
    await async_context_func()
