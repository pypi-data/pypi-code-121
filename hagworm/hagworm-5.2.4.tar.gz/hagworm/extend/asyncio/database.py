# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import asyncio
import aiomysql
import sqlalchemy

from contextvars import ContextVar

from aiomysql.sa import SAConnection, Engine
from aiomysql.sa.engine import _dialect as dialect

from pymysql.err import Warning, DataError, IntegrityError, ProgrammingError

from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.dml import Insert, Update, Delete

from motor.motor_asyncio import AsyncIOMotorClient

from .base import Utils, WeakContextVar, AsyncCirculator

from ..error import catch_error, MySQLReadOnlyError, MySQLClientDestroyed
from ..interface import AsyncContextManager


MONGO_POLL_WATER_LEVEL_WARNING_LINE = 0x10

MYSQL_ERROR_RETRY_COUNT = 0x10
MYSQL_POLL_WATER_LEVEL_WARNING_LINE = 0x10


class MongoPool:
    """Mongo连接管理
    """

    def __init__(
            self, host, username=None, password=None,
            *, name=None, auth_source=r'admin', min_pool_size=8, max_pool_size=32, max_idle_time=3600, wait_queue_timeout=10,
            compressors=r'zlib', zlib_compression_level=6,
            **settings
    ):

        self._name = name if name is not None else Utils.uuid1()[:8]

        settings[r'host'] = host
        settings[r'authSource'] = auth_source
        settings[r'minPoolSize'] = min_pool_size
        settings[r'maxPoolSize'] = max_pool_size
        settings[r'maxIdleTimeMS'] = max_idle_time * 1000
        settings[r'waitQueueTimeoutMS'] = wait_queue_timeout * 1000
        settings[r'compressors'] = compressors
        settings[r'zlibCompressionLevel'] = zlib_compression_level

        if username and password:
            settings[r'username'] = username
            settings[r'password'] = password

        self._pool = AsyncIOMotorClient(**settings)

        for server in self._servers.values():
            server.pool.remove_stale_sockets()

        self._pool_options = self._pool.options.pool_options

        Utils.log.info(
            f"Mongo {host} ({self._name}) initialized: "
            f"{self._pool_options.min_pool_size}/{self._pool_options.max_pool_size}"
        )

    @property
    def _servers(self):

        return self._pool.delegate._topology._servers

    def _echo_pool_info(self):

        global MONGO_POLL_WATER_LEVEL_WARNING_LINE

        for address, server in self._servers.items():

            free_size = len(server.pool.sockets)
            pool_size = free_size + server.pool.active_sockets
            max_pool_size = server.pool.max_pool_size

            if (max_pool_size - server.pool.active_sockets) < MONGO_POLL_WATER_LEVEL_WARNING_LINE:
                Utils.log.warning(
                    f'Mongo connection pool not enough ({self._name}){address}: '
                    f'{free_size}({pool_size}/{max_pool_size})'
                )
            else:
                Utils.log.debug(
                    f'Mongo connection pool info ({self._name}){address}: '
                    f'{free_size}({pool_size}/{max_pool_size})'
                )

    def reset(self):

        for address, server in self._servers.items():

            server.pool.reset()
            server.pool.remove_stale_sockets()

            Utils.log.info(
                f'Mongo connection pool reset {address}: {len(server.pool.sockets)}/{self._pool.max_pool_size}'
            )

    def close(self):

        if self._pool is not None:
            self._pool.close()
            self._pool = None

    def get_database(self, db_name):

        self._echo_pool_info()

        result = None

        with catch_error():
            result = self._pool[db_name]

        return result


class MongoDelegate:
    """Mongo功能组件
    """

    def __init__(self):

        self._mongo_pool = None

    async def async_init_mongo(self, *args, **kwargs):

        self._mongo_pool = MongoPool(*args, **kwargs)

    @property
    def mongo_pool(self):

        return self._mongo_pool

    async def mongo_health(self):

        result = False

        with catch_error():
            result = bool(await self._mongo_pool._pool.server_info())

        return result

    def reset_mongo_pool(self):

        self._mongo_pool.reset()

    def close_mongo_pool(self):

        self._mongo_pool.close()

    def get_mongo_database(self, db_name):

        return self._mongo_pool.get_database(db_name)

    def get_mongo_collection(self, db_name, collection):

        return self.get_mongo_database(db_name)[collection]


class MySQLPool:
    """MySQL连接管理
    """

    class _Connection(SAConnection):

        def __init__(self, connection, engine, compiled_cache=None):

            super().__init__(connection, engine, compiled_cache)

            if not hasattr(connection, r'build_time'):
                setattr(connection, r'build_time', Utils.loop_time())

        @property
        def build_time(self):

            return getattr(self._connection, r'build_time', 0)

        async def destroy(self):

            if self._connection is None:
                return

            if self._transaction is not None:
                await self._transaction.rollback()
                self._transaction = None

            self._connection.close()

            self._engine.release(self)
            self._connection = None
            self._engine = None

    def __init__(
            self, host, port, db, user, password,
            *, name=None, minsize=8, maxsize=32, echo=False, pool_recycle=21600,
            charset=r'utf8', autocommit=True, cursorclass=aiomysql.DictCursor,
            readonly=False, conn_life=43200,
            **settings
    ):

        self._name = name if name is not None else (Utils.uuid1()[:8] + (r'_ro' if readonly else r'_rw'))
        self._pool = None
        self._engine = None
        self._readonly = readonly
        self._conn_life = conn_life

        self._settings = settings

        self._settings[r'host'] = host
        self._settings[r'port'] = port
        self._settings[r'db'] = db

        self._settings[r'user'] = user
        self._settings[r'password'] = password

        self._settings[r'minsize'] = minsize
        self._settings[r'maxsize'] = maxsize

        self._settings[r'echo'] = echo
        self._settings[r'pool_recycle'] = pool_recycle
        self._settings[r'charset'] = charset
        self._settings[r'autocommit'] = autocommit
        self._settings[r'cursorclass'] = cursorclass

    @property
    def name(self):

        return self._name

    @property
    def readonly(self):

        return self._readonly

    @property
    def conn_life(self):

        return self._conn_life

    def __await__(self):

        self._pool = yield from aiomysql.create_pool(**self._settings).__await__()
        self._engine = Engine(dialect, self._pool)

        Utils.log.info(
            f"MySQL {self._settings[r'host']}:{self._settings[r'port']} {self._settings[r'db']}"
            f" ({self._name}) initialized: {self._pool.size}/{self._pool.maxsize}"
        )

        return self

    async def close(self):

        if self._pool is not None:

            self._pool.close()
            await self._pool.wait_closed()

            self._pool = None

    def _echo_pool_info(self):

        if self.health:
            Utils.log.debug(
                f'MySQL connection pool info ({self._name}): '
                f'{self._pool.freesize}({self._pool.size}/{self._pool.maxsize})'
            )
        else:
            Utils.log.warning(
                f'MySQL connection pool not enough ({self._name}): '
                f'{self._pool.freesize}({self._pool.size}/{self._pool.maxsize})'
            )

    @property
    def health(self):

        global MYSQL_POLL_WATER_LEVEL_WARNING_LINE

        return (self._pool.maxsize - self._pool.size + self._pool.freesize) > MYSQL_POLL_WATER_LEVEL_WARNING_LINE

    async def reset(self):

        if self._pool is not None:

            await self._pool.clear()

            Utils.log.info(
                f'MySQL connection pool reset ({self._name}): {self._pool.size}/{self._pool.maxsize}'
            )

    async def get_sa_conn(self):

        self._echo_pool_info()

        conn = await self._pool.acquire()

        return self._Connection(conn, self._engine)

    def get_client(self):

        client = None

        with catch_error():

            client = DBClient(self)

            if not self.health:
                client.set_auto_release(True)

        return client

    def get_transaction(self):

        result = None

        if self._readonly:
            raise MySQLReadOnlyError()

        with catch_error():
            result = DBTransaction(self)

        return result


class MySQLDelegate:
    """MySQL功能组件
    """

    def __init__(self):

        self._mysql_rw_pool = None
        self._mysql_ro_pool = None

        context_uuid = Utils.uuid1()

        self._mysql_client_context_switch = ContextVar(f'mysql_client_{context_uuid}_switch', default=True)

        self._mysql_rw_client_context = WeakContextVar(f'mysql_rw_client_{context_uuid}')
        self._mysql_ro_client_context = WeakContextVar(f'mysql_ro_client_{context_uuid}')

    @property
    def mysql_rw_pool(self):

        return self._mysql_rw_pool

    @property
    def mysql_ro_pool(self):

        return self._mysql_ro_pool
    @property
    def mysql_client_context_switch(self):

        return self._mysql_client_context_switch.get()

    @mysql_client_context_switch.setter
    def mysql_client_context_switch(self, val):

        return self._mysql_client_context_switch.set(val)

    async def async_init_mysql_rw(self, *args, **kwargs):

        self._mysql_rw_pool = await MySQLPool(*args, **kwargs)

    async def async_init_mysql_ro(self, *args, **kwargs):

        self._mysql_ro_pool = await MySQLPool(*args, **kwargs)

    async def async_close_mysql(self):

        if self._mysql_rw_pool is not None:
            await self._mysql_rw_pool.close()

        if self._mysql_ro_pool is not None:
            await self._mysql_ro_pool.close()

    async def mysql_health(self):

        result = await self._check_health(self._mysql_rw_pool)
        result &= await self._check_health(self._mysql_ro_pool)

        return result

    async def _check_health(self, pool):

        if pool is None:
            return True

        async with pool.get_client() as client:

            await client.safe_execute(r'select version();')

            return True

        return False

    async def reset_mysql_pool(self):

        if self._mysql_rw_pool:
            await self._mysql_rw_pool.reset()

        if self._mysql_ro_pool:
            await self._mysql_ro_pool.reset()

    def get_db_client(self, readonly=False, *, alone=False):

        client = None

        if alone or not self.mysql_client_context_switch:

            if readonly:
                if self._mysql_ro_pool is not None:
                    client = self._mysql_ro_pool.get_client()
                else:
                    client = self._mysql_rw_pool.get_client()
                    client._readonly = True
            else:
                client = self._mysql_rw_pool.get_client()

        else:

            if readonly:

                _client = self._mysql_rw_client_context.get()

                if _client is not None:
                    Utils.create_task(_client.release())

                client = self._mysql_ro_client_context.get()

                if client is None:

                    if self._mysql_ro_pool is not None:
                        client = self._mysql_ro_pool.get_client()
                    else:
                        client = self._mysql_rw_pool.get_client()
                        client._readonly = True

                    self._mysql_ro_client_context.set(client)

                else:

                    Utils.log.debug(r'Share mysql ro client in context')

            else:

                _client = self._mysql_ro_client_context.get()

                if _client is not None:
                    Utils.create_task(_client.release())

                client = self._mysql_rw_client_context.get()

                if client is None:

                    client = self._mysql_rw_pool.get_client()

                    self._mysql_rw_client_context.set(client)

                else:

                    Utils.log.debug(r'Share mysql rw client in context')

        return client

    def get_db_transaction(self):

        if self.mysql_client_context_switch:

            _client = self._mysql_rw_client_context.get()

            if _client is not None:
                Utils.create_task(_client.release())

            _client = self._mysql_ro_client_context.get()

            if _client is not None:
                Utils.create_task(_client.release())

        return self._mysql_rw_pool.get_transaction()


class _ClientBase:
    """MySQL客户端基类
    """

    @staticmethod
    def safestr(val):

        cls = type(val)

        if cls is str:
            val = aiomysql.escape_string(val)
        elif cls is dict:
            val = aiomysql.escape_dict(val)
        else:
            val = str(val)

        return val

    def __init__(self, pool):

        self._pool = pool
        self._conn = None

        self._readonly = pool.readonly
        self._auto_release = False

        self._lock = asyncio.Lock()

    @property
    def readonly(self):

        return self._readonly

    @property
    def insert_id(self):

        if self._conn:
            return self._conn.connection.insert_id()
        else:
            return None

    async def _get_conn(self):

        if self._pool is None:
            raise MySQLClientDestroyed()

        if self._conn is None:
            self._conn = await self._pool.get_sa_conn()

        return self._conn

    async def _close_conn(self, discard=False):

        if self._conn is not None:

            _conn, self._conn = self._conn, None

            if discard:
                await _conn.destroy()
            elif (Utils.loop_time() - _conn.build_time) > self._pool.conn_life:
                await _conn.destroy()
            else:
                await _conn.close()

    async def _execute(self, clause):

        raise NotImplementedError()

    async def execute(self, clause):

        result = None

        async with self._lock:
            result = await self._execute(clause)

        return result

    async def safe_execute(self, clause):

        async with self._lock:

            proxy = await self._execute(clause)
            await proxy.close()

            if self._auto_release:
                await self._close_conn()

    async def select(self, query, *multiparams, **params):

        result = []

        if not isinstance(query, Select):
            raise TypeError(r'Not sqlalchemy.sql.selectable.Select object')

        async with self._lock:

            proxy = await self._execute(query, *multiparams, **params)

            if proxy is not None:

                records = await proxy.cursor.fetchall()

                if records:
                    result.extend(records)

                if not proxy.closed:
                    await proxy.close()

            if self._auto_release:
                await self._close_conn()

        return result

    async def find(self, query, *multiparams, **params):

        result = None

        if not isinstance(query, Select):
            raise TypeError(r'Not sqlalchemy.sql.selectable.Select object')

        async with self._lock:

            proxy = await self._execute(query.limit(1), *multiparams, **params)

            if proxy is not None:

                record = await proxy.cursor.fetchone()

                if record:
                    result = record

                if not proxy.closed:
                    await proxy.close()

            if self._auto_release:
                await self._close_conn()

        return result

    async def count(self, table_col, select_where=None):

        _select = sqlalchemy.select([sqlalchemy.func.count(table_col).label(r'tbl_row_count')])

        if select_where is not None:
            _select = _select.where(select_where)

        result = await self.find(_select)

        return result[r'tbl_row_count']

    async def insert(self, query, *multiparams, **params):

        result = 0

        if self._readonly:
            raise MySQLReadOnlyError()

        if not isinstance(query, Insert):
            raise TypeError(r'Not sqlalchemy.sql.dml.Insert object')

        async with self._lock:

            proxy = await self._execute(query, *multiparams, **params)

            if proxy is not None:

                result = self.insert_id

                if not proxy.closed:
                    await proxy.close()

            if self._auto_release:
                await self._close_conn()

        return result

    async def update(self, query, *multiparams, **params):

        result = 0

        if self._readonly:
            raise MySQLReadOnlyError()

        if not isinstance(query, Update):
            raise TypeError(r'Not sqlalchemy.sql.dml.Update object')

        async with self._lock:

            proxy = await self._execute(query, *multiparams, **params)

            if proxy is not None:

                result = proxy.rowcount

                if not proxy.closed:
                    await proxy.close()

            if self._auto_release:
                await self._close_conn()

        return result

    async def delete(self, query, *multiparams, **params):

        result = 0

        if self._readonly:
            raise MySQLReadOnlyError()

        if not isinstance(query, Delete):
            raise TypeError(r'Not sqlalchemy.sql.dml.Delete object')

        async with self._lock:

            proxy = await self._execute(query, *multiparams, **params)

            if proxy is not None:

                result = proxy.rowcount

                if not proxy.closed:
                    await proxy.close()

            if self._auto_release:
                await self._close_conn()

        return result


class DBClient(_ClientBase, AsyncContextManager):
    """MySQL客户端对象，使用with进行上下文管理

    将连接委托给客户端对象管理，提高了整体连接的使用率

    """

    def set_auto_release(self, val):

        self._auto_release = val

    async def _context_release(self):

        await self._close_conn(self._lock.locked())

    async def release(self):

        async with self._lock:
            await self._close_conn()

    async def _execute(self, query, *multiparams, **params):

        global MYSQL_ERROR_RETRY_COUNT

        result = None

        async for times in AsyncCirculator(max_times=MYSQL_ERROR_RETRY_COUNT):

            try:

                conn = await self._get_conn()

                result = await conn.execute(query, *multiparams, **params)

            except (Warning, DataError, IntegrityError, ProgrammingError) as err:

                await self._close_conn(True)

                raise err

            except Exception as err:

                await self._close_conn(True)

                if times < MYSQL_ERROR_RETRY_COUNT:
                    Utils.log.error(err)
                else:
                    raise err

            else:

                break

        return result


class DBTransaction(_ClientBase, AsyncContextManager):
    """MySQL客户端事务对象，使用with进行上下文管理

    将连接委托给客户端对象管理，提高了整体连接的使用率

    """

    def __init__(self, pool):

        super().__init__(pool)

        self._trx = None

    async def _get_conn(self):

        if self._trx is None:
            self._conn = await super()._get_conn()
            self._trx = await self._conn.begin()

        return self._conn

    async def _close_conn(self, discard=False):

        if self._trx is not None:

            if self._trx.is_active:
                self._trx.close()

            self._trx = None

        await super()._close_conn(discard)

        self._pool = None

    async def _context_release(self):

        await self.rollback()

    async def release(self):

        await self.rollback()

    async def _execute(self, query, *multiparams, **params):

        result = None

        if self._readonly:
            raise MySQLReadOnlyError()

        try:

            conn = await self._get_conn()

            result = await conn.execute(query, *multiparams, **params)

        except Exception as err:

            await self._close_conn(True)

            raise err

        return result

    async def commit(self):

        async with self._lock:

            if self._trx:
                await self._trx.commit()

            await self._close_conn()

    async def rollback(self):

        async with self._lock:

            if self._trx:
                await self._trx.rollback()

            await self._close_conn()
