#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import re
import six
import sys
import traceback
import asyncio
import sqlalchemy
from sqlalchemy.orm import query, loading, attributes
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, AsyncConnection, create_async_engine
import sqlalchemy.databases as sqlalchemy_supported_engines
# from sqlalchemy.orm import sessionmaker
import motor.motor_asyncio
import motor
import sqlalchemy.sql.dml
from sqlalchemy.sql.expression import delete, insert

# from tornado.ioloop import IOLoop
# target_module = __import__('tornado.concurrent')
# if not hasattr(target_module.concurrent, 'return_future'):
#     setattr(target_module.concurrent, 'return_future', tornado.gen.coroutine)
# from motorengine import connect as mongo_connect
import mongoengine
import pymongo

from .sqlalchemy_dialects import asyncpg_migrate
from .sqlalchemy_dialects.sync_threading import AsyncioEngine as ThreadingAsyncioEngine

try:
    import asyncpg
except ImportError:
    pass
try:
    import aiomysql
except ImportError:
    pass
try:
    import aiosqlite
except ImportError:
    pass

try:
    import pymssql
except ImportError:
    pass
try:
    import cx_Oracle
    # import cx_Oracle_async
except ImportError:
    cx_Oracle = {}

from .supports import singleton
from .modelutils import model_columns, format_mongo_value, get_dbinstance_by_model, get_model_class_name, DEFAULT_SKIP_FIELDS
from .utilities import url_encode
from .exceptionreporter import ExceptionReporter

logging.getLogger('aiosqlite').setLevel(logging.INFO)
LOG = logging.getLogger('lycium.dbproxy')

supported_engines = [*sqlalchemy_supported_engines.__all__, 'cockroachdb']
supported_asyncio_engines = ['postgresql', 'mysql', 'cockroachdb', 'sqlite']

class _DbInstance(object):
    """
    """
    def __init__(self, name: str, engine: AsyncEngine, should_connect: bool = False) -> None:
        self.name: str = name
        self.engine: AsyncEngine = engine
        self.isconnecting: bool = False
        self.disconnected: bool = True
        self.conn: AsyncConnection = None
        if should_connect:
            self._start_connect()
        self.async_by_thread = False
        if hasattr(engine, 'async_by_thread'):
            self.async_by_thread = getattr(engine, 'async_by_thread')

    def onconnected(self, conn: AsyncConnection) -> None:
        self.disconnected = False
        self.isconnecting = False
        self.conn = conn

    def ondisconnected(self, reason: str, reconnect: bool = False) -> None:
        self.disconnected = True
        self.isconnecting = False
        if self.conn:
            self.conn.close()
            self.conn = None
        LOG.warn('db connection %s disconnected with reason:%s', self.name, reason)
        if reconnect:
            reconnect_secs = 2
            LOG.info('db connection %s will be reconnecting after %d seconds', self.name, reconnect_secs)
            asyncio.get_event_loop().call_later(reconnect_secs, self._connect_db)
            # IOLoop.current().call_later(reconnect_secs, self._connect_db)

    async def manual_connect(self):
        return await self._connect_db()

    async def _connect_db(self):
        if self.isconnecting:
            return
        url_info = self.engine.url
        auth_part = ''
        host_part = ''
        if url_info.username or url_info.password:
            auth_part = '%s:%s@' % ((url_info.username if url_info.username else ''), ('*' * len(url_info.password) if url_info.password else ''))
        if url_info.host:
            host_part = '%s:%d' % (url_info.host, url_info.port)
        connect_desc = '%s://%s%s/%s' % (url_info.drivername, auth_part, host_part, url_info.database)
        try:
            LOG.info('connecting database %s %s', self.name, connect_desc)
            t1 = time.time()
            self.isconnecting = True
            db_conn = await self.engine.connect()
            t2 = time.time()
            LOG.info('database %s connected in %.2f secs.', self.name, t2 - t1)
            self.onconnected(db_conn)
        except Exception as e:
            ExceptionReporter().report(key='DB-'+connect_desc, typ='CONNECT', 
                endpoint='%s|%s' % ('CONNECT', connect_desc),
                method='CONNECT',
                inputs=str(self.engine),
                outputs=str(e),
                content=traceback.format_exc(),
                level='ERROR'
            )
            self.ondisconnected(str(e), True)
    
    def _start_connect(self):
        try:
            loop = asyncio.get_event_loop()
        except Exception as e:
            LOG.info('get current asyncio event loop failed with error:%s, creates new event loop')
            loop = asyncio.new_event_loop()
        
        LOG.info('registering future %s connecting for %s in asyncio', self.engine.name, self.name)
        asyncio.run_coroutine_threadsafe(self._connect_db(), loop)

    def begin(self):
        return self.engine.begin()

@singleton
class DbProxy(object):
    """
    database agent component
    """
    def __init__(self):
        self.db_instances = {}
        self.default_mongo_db_instance = None
        self.default_rdbms_db_instance = None
        self._motor_count_documents_name = 'count_documents'

        if hasattr(motor.MotorCollection, 'count'):
            self._motor_count_documents_name = 'count'

        self._cur_execution_dbinstances = []

    def setup_rdbms(self, rdbms_configs: dict) -> bool:
        """Setup relational database configurations
        :param rdbms_configs:dict relational database configuration, it would skip the configuration named start with 'ignore'
            examples: {
                "local_storage": {
                    "connector": "sqlite",
                    "host": "./debug.sqlite.db",
                    "db": "main"
                },
                "remote_relational": {
                    "connector": "oracle",
                    "host": "127.0.0.1",
                    "port": 1521,
                    "user": "changeit",
                    "pwd": "changeit",      # password
                    "db": "changeit"
                },
                "ignore_relational": {      # the category name starts with 'ignore' characters would skip connecting
                    "connector": "mssql",
                    "host": "127.0.0.1",
                    "port": 1433,
                    "user": "changeit",
                    "pwd": "changeit",      # password
                    "db": "changeit"
                }
           }
        :return: bool
        """
        for k, dbconf in rdbms_configs.items():
            self.setup_rdbms_connection(k, dbconf)

    def setup_mongodbs(self, mongodb_configs: dict) -> bool:
        """Setup mongodb database configurations
        :param rdbms_configs:dict mongodb database configuration, it would skip the configuration named start with 'ignore'
            examples: {
                "ignore_mongo": {           # the category name starts with 'ignore' characters would skip connecting
                    "connector": "mongodb",
                    "host":  "127.0.0.1",
                    "port": 27017,
                    "user": "changeit",
                    "pwd": "changeit",      # password
                    "db": "changeit"
                }
            }
        :return: bool
        """
        for k, dbconf in mongodb_configs.items():
            self.setup_mongodb_connection(k, dbconf)

    def setup_rdbms_connection(self, category: str, dbconf: dict) -> bool:
        """Setup relational database configuration by configuration, the database instance would be named by category
        :param category:str name of rdbms configuration dict key
        :param dbconf:dict value of rdbms configuration element, contains keys of connector, host, port, user, pwd, db
            example: {
                    "connector": "oracle",
                    "host": "127.0.0.1",
                    "port": 1521,
                    "user": "changeit",
                    "pwd": "changeit",      # password
                    "db": "changeit"
                }
        :return: bool
        """
        engine = dbconf.get('connector', '')
        if engine not in supported_engines:
            LOG.error('setup rdbms connection with engine name:%s were not supported, skip it', engine)
            return False
        if category.startswith('ignore'):
            return False

        create_engine_params = {
            'encoding': dbconf.get('encoding', 'utf8'),
            'pool_pre_ping': True,
            # 'pool_use_lifo': True,
            'pool_timeout': 10,
            'pool_size': 7,
            'pool_recycle': 7200,
            # 'echo_pool': True,
            # 'echo': True,
            # 'strategy': ASYNCIO_STRATEGY,
            'connect_args': {
                # 'connect_timeout': 15,
                # 'timeout': 15
            }
        }
        if 'sqlite' == engine:
            del create_engine_params['pool_timeout']
            del create_engine_params['pool_size']
        if 'connect_args' in dbconf:
            connect_args = dbconf['connect_args'] 
            if not isinstance(connect_args, dict):
                s1 = str(connect_args).split('&')
                connect_args = {}
                for s2 in s1:
                    s3 = s2.split('=')
                    if len(s3) > 1:
                        connect_args[s3[0].strip()] = s3[1].strip()
            for k, v in connect_args.items():
                create_engine_params['connect_args'][k] = v

        conndsn = self.format_connection_string(dbconf)
        LOG.info('initializing database engine for %s', category)
        if engine in supported_asyncio_engines:
            db_engine = create_async_engine(conndsn, **create_engine_params)
        else:
            sync_engine = sqlalchemy.create_engine(conndsn, **create_engine_params)
            db_engine = ThreadingAsyncioEngine(sync_engine)
        db_inst = _DbInstance(category, db_engine, True)
        self.db_instances[category] = db_inst
        if not self.default_rdbms_db_instance:
            self.default_rdbms_db_instance = db_inst

        return True

    def setup_mongodb_connection(self, category: str, dbconf: dict) -> bool:
        """Setup mongodb database configuration by configuration, the database instance would be named by category
        :param category:str name of mongodb configuration dict key
        :param dbconf:dict value of mongodb configuration element, contains keys of connector, host, port, user, pwd, db
            example: {
                    "connector": "mongodb",
                    "host":  "127.0.0.1",
                    "port": 27017,
                    "user": "changeit",
                    "pwd": "changeit",      # password
                    "db": "changeit"
                }
        :return: bool
        """
        if category.startswith('ignore'):
            return False
        conndsn = self.format_connection_string(dbconf)
        mongo_cli = motor.motor_asyncio.AsyncIOMotorClient(conndsn)
        mongo_db = mongo_cli[dbconf.get('db')]
        LOG.info('mongodb %s %s setupped', category, str(mongo_cli.address))
        db_inst = _DbInstance(category, mongo_cli, False)
        db_inst.disconnected = True
        db_inst.conn = mongo_db
        if not self.default_mongo_db_instance:
            self.default_mongo_db_instance = db_inst
        self.db_instances[category] = db_inst
        return True

    def format_connection_string(self, dbconf: dict) -> str:
        """Formats database connection sqlalchemy formation dsn string
        :param dbconf:dict value of mongodb configuration element, contains keys of connector, host, port, user, pwd, db
        :return:str example: postgresql+asyncpg://user:password@host:port/db
        """
        engine = dbconf.get('connector', 'mysql')
        user = dbconf.get('user', 'guest')
        pwd = dbconf.get('pwd', '')
        host = dbconf.get('host', 'localhost')
        port = int(dbconf.get('port', 3306))
        dbname = dbconf.get('db', 'guest')
        driverpart = dbconf.get('driver', '')
        if driverpart:
            driverpart = '+' + driverpart
        ext_params = ''
        if dbconf.get('ext_args'):
            ext_args = [f'{ext_arg_name}={ext_arg_value}' for ext_arg_name, ext_arg_value in
                        dbconf.get('ext_args', {}).items()]
            ext_params = f'?{"&".join(ext_args)}'
        if 'cockroachdb' == engine:
            engine = 'postgresql'
            driverpart = '+asyncpg'
        elif 'postgresql' == engine:
            driverpart = '+asyncpg'
        elif 'mysql' == engine:
            driverpart = '+aiomysql'
        elif 'sqlite' == engine:
            driverpart = '+aiosqlite'
        elif 'oracle' == engine:
            driverpart = '+cx_oracle'
        elif 'mssql' == engine:
            driverpart = '+pymssql'

        connection_str = ''
        if 'oracle' == engine:
            if sys.platform == 'darwin':
                connection_str = "%s%s://%s:%s@%s:%d/%s%s" % (engine, driverpart, url_encode(user), url_encode(pwd), host, port, dbname, ext_params)
            else:
                connection_str = "%s%s://%s:%s@%s:%d/%s%s" % (engine, driverpart, url_encode(user), url_encode(pwd), host, port, dbname, ext_params)
                # ora_dsn = cx_Oracle.makedsn(host, port, service_name=dbname)
                # connection_str = "%s%s://%s:%s@%s%s" % (engine, driverpart, user, url_encode(pwd), ora_dsn, ext_params)
        elif 'sqlite' == engine:
            connection_str = '%s%s:///%s' % (engine, driverpart, host)
        else:
            connection_str = '%s%s://%s:%s@%s:%d/%s%s' % (engine, driverpart, url_encode(user), url_encode(pwd), host, port, dbname, ext_params)

        return connection_str

    def get_mongo_dbinstance(self, model) -> _DbInstance:
        """Get mongodb database instance by orm model
        :param model:modelutils.MongoBase implemented mongodb orm model
        :return: _DbInstance 
        """
        model_name = get_model_class_name(model)
        dbflag = get_dbinstance_by_model(model_name)
        if dbflag:
            if dbflag in self.db_instances:
                return self.db_instances[dbflag]
            else:
                LOG.error('query model:%s while could not determine the database instance', model_name)
                raise Exception('model %s configured db instance %s were not exists', model_name, dbflag)
        return self.default_mongo_db_instance

    def get_model_dbinstance(self, model) -> _DbInstance:
        """Get mongodb database instance by orm model
        :param model:modelutils.ModelBase sqlalchemy.ext.declarative.declarative_base implemented rdbms orm model
        
        :return: _DbInstance 
        """
        model_name = model if isinstance(model, str) else str(model._sa_class_manager.class_.__name__)
        dbflag = get_dbinstance_by_model(model_name)
        if dbflag:
            if dbflag in self.db_instances:
                return self.db_instances[dbflag]
            else:
                LOG.error('query model:%s while could not determine the database instance', model_name)
                raise Exception('model %s configured db instance %s were not exists', model_name, dbflag)
        return self.default_rdbms_db_instance

    def get_dbinstance(self, category: str) -> _DbInstance:
        """Get database instance by database category name
        :param category:str database category name configured by rdbms configurations
        
        :return: _DbInstance 
        """
        if category:
            if category in self.db_instances:
                return self.db_instances[category]
            else:
                LOG.error('could not get the database instance %s', category)
                raise Exception('db instance %s were not exists', category)
        return self.default_rdbms_db_instance

    ################ part of rdbms operations ################
    # common queries
    async def query_list(self, model, filters, limit, offset, sort, direction, selections=None, joins=None):
        """RDBMS query list by orm model
        :param model:modelutils.ModelBase sqlalchemy.ext.declarative.declarative_base implemented rdbms orm model
        :param filters:list|dict|tuple filter conditions
        :param limit:int returning rows limit
        :param offset:int rows offset in database
        :param sort:str sorting database table column
        :param direction:str sorting order, should be one of (asc|desc)
        :param selections:list select fields instead of all model fields
        :param joins:list multi table join condition
        :return :list, int returns list of current queried rows and total records in database
        """
        qry, dbinstance, columns, _ = self._format_rdbms_query(model, filters, sort, direction, joins=joins)
        
        total = await self._execute_rdbms_query_count(dbinstance, qry)
        if not total:
            return [], total

        qry = qry.limit(limit).offset(offset)
        if selections:
            _selections = []
            for col in selections:
                if isinstance(col, str):
                    _selections.append(getattr(model, col))
                else:
                    _selections.append(col)
            qry = qry.with_entities(*_selections)
        rows = await self._execute_rdbms_result(dbinstance, qry, fetch_all=True)

        items = []
        if selections:
            for row in rows:
                item = {}
                for k in selections:
                    col_name = k if isinstance(k, str) else k.key
                    item[col_name] = row._data[row._keymap[getattr(model, col_name).expression._label][1]]
                items.append(item)
        else:
            for row in rows:
                item = {}
                for k in columns:
                    if k in DEFAULT_SKIP_FIELDS:
                        continue
                    item[k] = row._data[row._keymap[getattr(model, k).expression._label][1]]
                items.append(item)

        return items, total

    def _format_rdbms_query(self, model, filters, sort, direction, joins=None):
        columns,pk = model_columns(model)
        dbinstance = self.get_model_dbinstance(model)
        engine_name = dbinstance.engine.dialect.name
        orderby = None
        if sort:
            if direction == 'desc':
                orderby = sqlalchemy.desc(getattr(model, sort))
            else:
                orderby = sqlalchemy.asc(getattr(model, sort))
        elif (engine_name == 'mssql' or engine_name == 'postgresql'):
            if pk:
                orderby = getattr(model, pk)
            else:
                orderby = getattr(model, columns[0])
        
        qry = query.Query(model)
        if joins:
            for join in joins:
                qry = qry.join(*join)
        qry = qry.filter(*filters)
        if isinstance(orderby, list):
            qry = qry.order_by(*orderby)
        elif orderby is not None:
            qry = qry.order_by(orderby)
        return qry, dbinstance, columns, pk

    async def query_all(self, model, filters, sort=None, direction='asc', joins=None):
        qry, dbinstance, columns, _ = self._format_rdbms_query(model, filters, sort, direction, joins=joins)
        
        rows = await self._execute_rdbms_result(dbinstance, qry, fetch_all = True)
        items = []
        for row in rows:
            item = {}
            for k in columns:
                if k in DEFAULT_SKIP_FIELDS:
                    continue
                item[k] = row._data[row._keymap[getattr(model, k).expression._label][1]]
            items.append(item)

        return items

    async def _execute_rdbms_result(self, dbinstance: _DbInstance, qry: query.Query, fetch_all: bool = False, fetch_one: bool = False, execution_options: dict = sqlalchemy.util.EMPTY_DICT, sql_params = None):
        query_statement = ''
        query_params = None
        if isinstance(qry, query.Query):
            querycontext = qry.with_labels()._compile_context()
            if hasattr(querycontext, 'statement'):
                # querycontext.statement.use_labels = True
                query_statement = querycontext.statement
            else:
                query_statement = querycontext.query
            query_params = qry._params
        elif isinstance(qry, str):
            query_statement = sqlalchemy.text(qry)
            query_params = sql_params
        else:
            query_statement = qry
            if hasattr(qry, '_params'):
                query_params = qry._params
        if dbinstance.disconnected:
            await dbinstance.manual_connect()
            if dbinstance.disconnected:
                LOG.error('execute query [%s] on db connection %s while the connection were not connected.', str(query_statement), dbinstance.name)
                raise Exception('Connection by %s were not connected' % dbinstance.name)
        ret = None
        start_ts = time.time()
        try:
            # asyncio with threading like oracle, mssql:
            if dbinstance.async_by_thread:
                async with dbinstance.engine.begin() as conn:
                    async with conn.begin():
                        if query_params is None:
                            cursor = await conn.execute(query_statement, execution_options=execution_options)
                        else:
                            cursor = await conn.execute(query_statement, parameters=query_params, execution_options=execution_options)
                        execute_ts = time.time()
                        if execute_ts - 1 > start_ts:
                            LOG.warn('Slow query, execute query [%s] on db connection %s had taken too much time (%.2fs) on start time:[%s]', str(query_statement), dbinstance.name, execute_ts - start_ts, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_ts)))
                        fetched_ts = 0
                        # if query_statement.is_insert or query_statement.is_update or query_statement.is_delete:
                        #     await conn.commit()
                        if fetch_all:
                            if asyncio.iscoroutinefunction(cursor.fetchall):
                                ret = await cursor.fetchall()
                            else:
                                ret = cursor.fetchall()
                            fetched_ts = time.time()
                        elif fetch_one:
                            if asyncio.iscoroutinefunction(cursor.fetchone):
                                ret = await cursor.fetchone()
                            else:
                                ret = cursor.fetchone()
                            fetched_ts = time.time()
                        else:
                            ret = cursor
            else:
                async with AsyncSession(dbinstance.engine) as session:
                    if query_params is None:
                        cursor = await session.execute(query_statement, execution_options=execution_options)
                    else:
                        cursor = await session.execute(query_statement, params=query_params, execution_options=execution_options)
                    execute_ts = time.time()
                    if execute_ts - 1 > start_ts:
                        LOG.warn('Slow query, execute query [%s] on db connection %s had taken too much time (%.2fs) on start time:[%s]', str(query_statement), dbinstance.name, execute_ts - start_ts, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_ts)))
                    fetched_ts = 0
                    if query_statement.is_insert or query_statement.is_update or query_statement.is_delete:
                        await session.commit()
                    if fetch_all:
                        if asyncio.iscoroutinefunction(cursor.all):
                            ret = await cursor.all()
                        else:
                            ret = cursor.all()
                        fetched_ts = time.time()
                    elif fetch_one:
                        if asyncio.iscoroutinefunction(cursor.one):
                            ret = await cursor.one_or_none()
                        else:
                            ret = cursor.one_or_none()
                        fetched_ts = time.time()
                    else:
                        ret = cursor
            if fetched_ts and (fetched_ts - 1 > execute_ts):
                LOG.warn('Slow query fetching, execute query [%s] on db connection %s fetching %s results had taken too much time (%.2fs) on fetching time:[%s]', str(query_statement), dbinstance.name, ('all' if fetch_all else 'one'), fetched_ts - execute_ts, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(execute_ts)))
        except sqlalchemy.exc.OperationalError as e:
            LOG.error('query sql %s failed with error(%s):%s', str(query_statement), str(e.code), str(e))
            ExceptionReporter().report(key='SQL-'+str('query'), typ='SQL', 
                endpoint='%s|%s' % (str(dbinstance.name), str(query_statement)),
                method='QUERY',
                inputs=str(query_statement),
                outputs='',
                content=str(e),
                level='ERROR'
            )
            if e.connection_invalidated:
                dbinstance.ondisconnected(str(e), True)
            raise e
        except sqlalchemy.exc.DatabaseError as e:
            LOG.error('query sql %s failed with error(%s):%s', str(query_statement), str(e.code), str(e))
            ExceptionReporter().report(key='SQL-'+str('query'), typ='SQL', 
                endpoint='%s|%s' % (str(dbinstance.name), str(query_statement)),
                method='QUERY',
                inputs=str(query_statement),
                outputs='',
                content=str(e),
                level='ERROR'
            )
            if True or e.connection_invalidated:
                dbinstance.ondisconnected(str(e), True)
            raise e
        except Exception as e:
            LOG.error('query sql %s failed with error:%s', str(query_statement), str(e))
            ExceptionReporter().report(key='SQL-'+str('query'), typ='SQL', 
                endpoint='%s|%s' % (str(dbinstance.name), str(query_statement)),
                method='QUERY',
                inputs=str(query_statement),
                outputs='',
                content=str(e),
                level='ERROR'
            )
            raise e
        return ret

    async def _execute_rdbms_query_count(self, dbinstance: _DbInstance, qry: query.Query):
        col = sqlalchemy.sql.func.count(sqlalchemy.sql.literal_column("*"))
        qrycount = qry.from_self(col)
        # querycontext = qrycount._compile_context()
        # querycontext.statement.use_labels = True
        ret = await self._execute_rdbms_result(dbinstance, qrycount, fetch_one = True)
        if ret:
            return ret[0]
        return 0

    async def find_item(self, model, filters):
        dbinstance = self.get_model_dbinstance(model)
        qry = query.Query(model).filter(*filters)
        row = await self._execute_rdbms_result(dbinstance, qry, fetch_one=True)
        if not row:
            return None
        item = model()
        columns, _ = model_columns(model)            
        for k in columns:
            setattr(item, k, row._data[row._keymap[getattr(model, k).expression._label][1]])
        return item

    async def get_count(self, model, filters):
        dbinstance = self.get_model_dbinstance(model)
        qry = query.Query(model).filter(*filters)
        count = await self._execute_rdbms_query_count(dbinstance, qry)
        return count

    async def update_values(self, model, filters, values: dict):
        dbinstance = self.get_model_dbinstance(model)
        stmt = sqlalchemy.update(model).filter(*filters).values(**values)
        result = await self._execute_rdbms_result(dbinstance, stmt, execution_options={'synchronize_session': False})
        if result and result.rowcount:
            return result.rowcount
            
        return 0

    async def update_item(self, item):
        model = item.__class__
        columns, pk = model_columns(model)
        dbinstance = self.get_model_dbinstance(model)
        values, defaults = self.get_rdbms_instance_update_values(item, model, columns, pk)
        if not values:
            return False
        stmt = sqlalchemy.update(model).filter(getattr(model, pk)==getattr(item, pk)).values(**values)
        result = await self._execute_rdbms_result(dbinstance, stmt)
        if result and result.rowcount:
            for k, v in defaults.items():
                setattr(item, k, v)
            
        return item

    async def insert_item(self, item, auto_flush=False):
        model = item.__class__
        columns, pk = model_columns(model)
        dbinstance = self.get_model_dbinstance(model)
        values, defaults = self.get_rdbms_instance_insert_values(item, model, columns, pk)
        if not values:
            return False
        stmt = sqlalchemy.insert(model).values(**values)
        result = await self._execute_rdbms_result(dbinstance, stmt)
        if result and result.rowcount:
            for k, v in defaults.items():
                setattr(item, k, v)
            if result.inserted_primary_key:
                setattr(item, pk, result.inserted_primary_key[0])
            
        return item

    async def insert_items(self, items, auto_flush=False):
        if not items:
            return None
        insert_groups = {}
        for item in items:
            model = item.__class__
            if model not in insert_groups:
                insert_groups[model] = []
            insert_groups[model].append(item)
        for model, insert_group in insert_groups.items():
            columns, pk = model_columns(model)
            dbinstance = self.get_model_dbinstance(model)
            if 'oracle' == dbinstance.engine.name:
                try:
                    if len(insert_group) > 10:
                        LOG.warning('insert items of %s count:%d for %s that the engine does not support batch inserts, this would take a long time', str(model.__name__), len(insert_group), dbinstance.engine.name)
                    cur_group = []
                    insert_batches = []
                    i = 0
                    for item in insert_group:
                        cur_group.append(item)
                        i += 1
                        if i > 99:
                            insert_batches.append(cur_group)
                            cur_group = []
                            i = 0
                    if i > 0:
                        insert_batches.append(cur_group)
                    i = 1
                    for insert_batch in insert_batches:
                        async with AsyncSession(dbinstance.engine) as session:
                            LOG.info('inserting items of %s by count:%d on batch:%d', str(model.__name__), len(insert_batch), i)
                            t01 = time.time()
                            async with session.begin():
                                for item in insert_batch:
                                    session.add(item)
                            await session.commit()
                            t02 = time.time()
                            LOG.info('inserted items of %s by count:%d on batch:%d taken %.2f secs', str(model.__name__), len(insert_batch), i, t02 - t01)
                            i += 1
                except sqlalchemy.exc.OperationalError as e:
                    LOG.error('query insert items of %s failed with error(%s):%s', str(model.__name__), str(e.code), str(e))
                    ExceptionReporter().report(key='SQL-'+str('INSERT'), typ='SQL', 
                        endpoint='%s|%s' % (str(dbinstance.name), str(model.__name__)),
                        method='INSERT',
                        inputs=str(model.__name__),
                        outputs=str(e),
                        content=str(traceback.format_exc()),
                        level='ERROR'
                    )
                    if e.connection_invalidated:
                        dbinstance.ondisconnected(str(e), True)
                    raise e
                except sqlalchemy.exc.DatabaseError as e:
                    LOG.error('query insert items of %s failed with error(%s):%s', str(model.__name__), str(e.code), str(e))
                    ExceptionReporter().report(key='SQL-'+str('INSERT'), typ='SQL', 
                        endpoint='%s|%s' % (str(dbinstance.name), str(model.__name__)),
                        method='INSERT',
                        inputs=str(model.__name__),
                        outputs=str(e),
                        content=str(traceback.format_exc()),
                        level='ERROR'
                    )
                    if True or e.connection_invalidated:
                        dbinstance.ondisconnected(str(e), True)
                    raise e
                except Exception as e:
                    LOG.error('query insert items of %s failed with error:%s', str(model.__name__), str(e))
                    ExceptionReporter().report(key='SQL-'+str('INSERT'), typ='SQL', 
                        endpoint='%s|%s' % (str(dbinstance.name), str(model.__name__)),
                        method='INSERT',
                        inputs=str(model.__name__),
                        outputs=str(e),
                        content=str(traceback.format_exc()),
                        level='ERROR'
                    )
                    raise e
                continue
            total_idx = len(insert_group)
            if total_idx > 1000:
                start_idx = 0
                end_idx = 500
                LOG.warning('insert items of %s count:%d too large, split the operation in batch of %d', model.__name__, total_idx, end_idx)
                while end_idx <= total_idx:
                    insert_values = []
                    # insert_defaults = []
                    for i in range(start_idx, end_idx):
                        values, defaults = self.get_rdbms_instance_insert_values(insert_group[i], model, columns, pk)
                        insert_values.append(values)
                        # insert_defaults.append(defaults)

                    stmt = sqlalchemy.insert(model).values(insert_values)
                    result = await self._execute_rdbms_result(dbinstance, stmt)
                    # for i in range(start_idx, end_idx):
                    #     for k, v in insert_defaults[i].items():
                    #         setattr(insert_group[i], k, v)
                    #     if result.inserted_primary_key:
                    #         setattr(insert_group[i], pk, result.inserted_primary_key[i-start_idx])
                    
                    start_idx = end_idx
                    end_idx = end_idx + 500
                    if end_idx > total_idx:
                        end_idx = total_idx
                    if start_idx >= end_idx:
                        break
            else:
                insert_values = []
                # insert_defaults = []
                for i in range(0, total_idx):
                    values, defaults = self.get_rdbms_instance_insert_values(insert_group[i], model, columns, pk)
                    insert_values.append(values)
                    # insert_defaults.append(defaults)

                stmt = sqlalchemy.insert(model).values(insert_values)
                result = await self._execute_rdbms_result(dbinstance, stmt)
            
        return True

    async def del_item(self, item):
        model = item.__class__
        dbinstance = self.get_model_dbinstance(model)
        _, pk = model_columns(model)
        stmt = sqlalchemy.delete(model).where(getattr(model, pk)==getattr(item, pk))
        result = await self._execute_rdbms_result(dbinstance, stmt)
        if result and result.rowcount:
            return result.rowcount
            
        return 0

    async def del_items(self, model, filters):
        dbinstance = self.get_model_dbinstance(model)
        stmt = sqlalchemy.delete(model).where(*filters)
        result = await self._execute_rdbms_result(dbinstance, stmt, execution_options={'synchronize_session': False})
        if result and result.rowcount:
            return result.rowcount
            
        return 0

    def get_rdbms_instance_insert_values(self, item, model, columns, pk):
        values = {}
        defaults = {}
        for col in columns:
            tbl_col_name = getattr(model, col).expression.name
            if col in item._sa_instance_state.unmodified:
                v = self.get_rdbms_instance_default_value(getattr(model, col).expression, True)
                if v is None and col == pk:
                    continue
                values[tbl_col_name] = v
                defaults[tbl_col_name] = v
            else:
                values[tbl_col_name] = getattr(item, col)
        return values, defaults

    def get_rdbms_instance_update_values(self, item, model, columns, pk):
        values = {}
        defaults = {}
        for col in columns:
            if col == pk:
                continue
            # tbl_col_name = getattr(model, col).expression.name
            values[col] = getattr(item, col)
            v = self.get_rdbms_instance_default_value(getattr(model, col).expression, False)
            if v is not None:
                values[col] = v
                defaults[col] = v
            
        return values, defaults

    def get_rdbms_instance_default_value(self, column, is_insert):
        column_default = column.default if is_insert else column.onupdate
        if column_default is None:
            return None
        else:
            return self._exec_rdbms_default(column, column_default, column.type)

    def _exec_rdbms_default(self, column, default, type_):
        if default.is_sequence:
            # raise Exception("sequence default column value is not supported")
            return None # self.fire_sequence(default, type_)
        elif default.is_callable:
            return default.arg(None)
        elif default.is_clause_element:
            # TODO: expensive branching here should be
            raise Exception("clause default column value is not supported")
            # # pulled into _exec_scalar()
            # conn = self.connection
            # if not default._arg_is_typed:
            #     default_arg = expression.type_coerce(default.arg, type_)
            # else:
            #     default_arg = default.arg
            # c = expression.select([default_arg]).compile(bind=conn)
            # return conn._execute_compiled(c, (), {}).scalar()
            return None
        else:
            return default.arg

    async def exec_query(self, db_category, sql, arguments: dict = None):
        """
        execute sql for orm dbs
        """
        if (not sql):
            return []
        dbinst: _DbInstance = self.get_dbinstance(db_category)
        # t1 = time.time()
        rows = await self._execute_rdbms_result(dbinst, sql, fetch_all=True, sql_params=arguments)
        # t2 = time.time()
        # print("------>>>>> %.2f executing [%s] from [%s] to [%s]" % (t2 - t1, str(sql), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t1)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t2))))
        return rows

    async def exec_update(self, db_category, sql, arguments: dict = None):
        """
        execute sql for no back, update or insert
        """
        if (not sql):
            return False
        dbinstance: _DbInstance = self.get_dbinstance(db_category)
        sql_stmt = sqlalchemy.text(sql)
        sql_stmt.is_update = True
        await self._execute_rdbms_result(dbinstance, sql_stmt, execution_options={'synchronize_session': False}, sql_params=arguments)
        return True
    
    # call db procedure
    async def call_procedure(self, db_category, proc_name, params, out_params=None):
        dbinstance: _DbInstance = self.get_dbinstance(db_category)
        if dbinstance.disconnected:
            await dbinstance.manual_connect()
            if dbinstance.disconnected:
                LOG.error('call procedure [%s] on db connection %s while the connection were not connected.', proc_name, db_category)
                raise Exception('Connection by %s were not connected', db_category)
        if not isinstance(params, list):
            return False
        conn = await dbinstance.engine.raw_connection()
        cursor = conn.cursor()
        result_values = {}
        if out_params and isinstance(out_params, dict) and 'oracle' == dbinstance.engine.sync_engine.name:
            for k, v in out_params.items():
                result_values[k] = cursor.var(getattr(cx_Oracle, v))
            params.extend(result_values.values())
        else:
            result_values = []
        # 调用存储过程
        cursor.callproc(proc_name, params)
        if isinstance(result_values, dict):
            result = {k:int(result_values[k].getvalue()) if out_params.get(k) in ['NUMBER', 'INTEGER', 'INT'] and result_values[k].getvalue() is not None 
                else result_values[k].getvalue() for k in result_values}
        else:
            result = []
            for cursor_result in cursor.stored_results():
                result.append(cursor_result.fetchall())
        
        cursor.close()
        return result
    ################ end part of rdbms operations ################

    ################ part of mongodb operations ################
    async def query_list_mongo(self, model, filters, limit, offset, sort, direction, selections=None, joins=None, as_dict=True):
        q = self._format_mongo_query(model, filters)
        if selections:
            selFields = {}
            for k in selections:
                selFields[k] = 1
            if selFields:
                q = q.fields(*selFields)
        # if sort:
        #     if direction.lower() == 'desc':
        #         q = q.order_by('-'+sort)
        #     else:
        #         q = q.order_by(sort)
        if joins:
            # TODO
            pass

        collection = self._prepare_mongo_collection(model)
        total = await getattr(collection, self._motor_count_documents_name)(q._query)

        q = q.skip(offset)

        if sort:
            direc = pymongo.ASCENDING
            if direction.lower() == 'desc':
                direc = pymongo.DESCENDING
            cursor = collection.find(q._query).sort(sort, direc)
        else:
            cursor = collection.find(q._query)
        rows = await cursor.to_list(length=limit)

        items = []
        if as_dict:
            if selections:
                for row in rows:
                    item = {model._reverse_db_field_map[k] if k in model._reverse_db_field_map else k: format_mongo_value(v) for k, v in row.items() if k in selections}
                    items.append(item)
            else:
                for row in rows:
                    item = {model._reverse_db_field_map[k] if k in model._reverse_db_field_map else k: format_mongo_value(v) for k, v in row.items() if k not in DEFAULT_SKIP_FIELDS}
                    items.append(item)
        else:
            conditions = {}
            prepare_items = {}
            for row in rows:
                item = model()
                for k, v in row.items():
                    attr = model._reverse_db_field_map[k] if k in model._reverse_db_field_map else k
                    if isinstance(model._fields.get(attr), mongoengine.fields.ReferenceField):
                        field = model._fields.get(attr)
                        ref_doc_type = field.document_type
                        pk = ref_doc_type._reverse_db_field_map.get('_id')
                        if pk:
                            if attr not in conditions:
                                conditions[attr] = {'filters': {pk+'__in': []}, 'ref_doc_type': ref_doc_type}
                            if attr not in prepare_items:
                                prepare_items[attr] = {v: []}
                            elif v not in prepare_items[attr]:
                                prepare_items[attr][v] = []
                            conditions[attr]['filters'][pk+'__in'].append(v)
                            prepare_items[attr][v].append(item)
                    
                    setattr(item, attr, v)
                items.append(item)

            if conditions:
                for attr, ref_options in conditions.items():
                    ref_rows = await self.query_all_mongo(ref_options['ref_doc_type'], ref_options['filters'], limit=limit, as_dict=as_dict)
                    for ref_row in ref_rows:
                        if ref_row.id in prepare_items[attr]:
                            for dst_item in prepare_items[attr][ref_row.id]:
                                setattr(dst_item, attr, ref_row)
        
        return items, total

    async def query_all_mongo(self, model, filters, limit=100, sort=None, **kwargs):
        direction = kwargs.pop('direction', None)
        selections = kwargs.pop('selections', None)
        joins = kwargs.pop('joins', None)
        as_dict = kwargs.pop('as_dict', True)
        q = self._format_mongo_query(model, filters)
        if selections:
            selFields = {}
            for k in selections:
                selFields[k] = 1
            if selFields:
                q = q.fields(*selFields)
        # if sort:
        #     if direction.lower() == 'desc':
        #         q = q.order_by('-'+sort)
        #     else:
        #         q = q.order_by(sort)
        if joins:
            # TODO
            pass

        collection = self._prepare_mongo_collection(model)

        if sort:
            direc = pymongo.ASCENDING
            if direction.lower() == 'desc':
                direc = pymongo.DESCENDING
            cursor = collection.find(q._query).sort(sort, direc)
        else:
            cursor = collection.find(q._query)
        rows = await cursor.to_list(length=limit)

        items = []
        if as_dict:
            if selections:
                for row in rows:
                    item = {model._reverse_db_field_map[k] if k in model._reverse_db_field_map else k: v for k, v in row.items() if k in selections}
                    items.append(item)
            else:
                for row in rows:
                    item = {model._reverse_db_field_map[k] if k in model._reverse_db_field_map else k: v for k, v in row.items() if k not in DEFAULT_SKIP_FIELDS}
                    items.append(item)
        else:
            conditions = {}
            prepare_items = {}
            for row in rows:
                item = model()
                for k, v in row.items():
                    attr = model._reverse_db_field_map[k] if k in model._reverse_db_field_map else k
                    if isinstance(model._fields.get(attr), mongoengine.fields.ReferenceField):
                        field = model._fields.get(attr)
                        ref_doc_type = field.document_type
                        pk = ref_doc_type._reverse_db_field_map.get('_id')
                        if pk:
                            if attr not in conditions:
                                conditions[attr] = {'filters': {pk+'__in': []}, 'ref_doc_type': ref_doc_type}
                            if attr not in prepare_items:
                                prepare_items[attr] = {v: []}
                            elif v not in prepare_items[attr]:
                                prepare_items[attr][v] = []
                            conditions[attr]['filters'][pk+'__in'].append(v)
                            prepare_items[attr][v].append(item)
                    
                    setattr(item, attr, v)
                items.append(item)

            if conditions:
                for attr, ref_options in conditions.items():
                    ref_rows = await self.query_all_mongo(ref_options['ref_doc_type'], ref_options['filters'], limit=limit, as_dict=as_dict)
                    for ref_row in ref_rows:
                        if ref_row.id in prepare_items[attr]:
                            for dst_item in prepare_items[attr][ref_row.id]:
                                setattr(dst_item, attr, ref_row)

        return items

    async def find_one_mongo(self, model, *args, **kwargs):
        """
        """
        as_dict = kwargs.pop('as_dict', False)
        q = self._format_mongo_query(model, (args, kwargs))
        collection = self._prepare_mongo_collection(model)
        document = await collection.find_one(q._query)
        if not document:
            return None

        if as_dict:
            item = {model._reverse_db_field_map[k] if k in model._reverse_db_field_map else k: v for k, v in document.items()}
            # for k1, k2 in model._reverse_db_field_map.items():
            #     item[k2] = format_mongo_value(document.get(k1))
            return item
        else:
            item = model()
            for k, v in document.items():
                attr = model._reverse_db_field_map[k] if k in model._reverse_db_field_map else k
                if isinstance(model._fields.get(attr), mongoengine.fields.ReferenceField):
                    field = model._fields.get(attr)
                    ref_doc_type = field.document_type
                    pk = ref_doc_type._reverse_db_field_map.get('_id')
                    if pk:
                        ref_filters = {pk: v, 'as_dict': as_dict}
                        v = await self.find_one_mongo(ref_doc_type, **ref_filters)

                setattr(item, attr, v)

        return item

    async def mongo_aggregate(self, model, pipeline=[], *args, **kwargs):
        """
        query mongo by aggregate.
        """
        as_dict = kwargs.pop('as_dict', True)
        collection = self._prepare_mongo_collection(model)
        cursor = collection.aggregate(pipeline)
        data_list = []
        if as_dict:
            while (await cursor.fetch_next):
                item = cursor.next_object()
                data_list.append(item)
        else:
            while (await cursor.fetch_next):
                item = cursor.next_object()
                obj = model()
                for k, v in item.items():
                    attr = model._reverse_db_field_map[k] if k in model._reverse_db_field_map else k
                    if isinstance(model._fields.get(attr), mongoengine.fields.ReferenceField):
                        field = model._fields.get(attr)
                        ref_doc_type = field.document_type
                        pk = ref_doc_type._reverse_db_field_map.get('_id')
                        if pk:
                            ref_filters = {pk: v, 'as_dict': as_dict}
                            v = await self.find_one_mongo(ref_doc_type, **ref_filters)

                    setattr(obj, attr, v)
                data_list.append(obj)

        return data_list

    async def save_mongo(self, item, force_insert=False, validate=True, clean=True,
             write_concern=None, cascade=None, cascade_kwargs=None,
             _refs=None, save_condition=None, signal_kwargs=None, **kwargs):
        """Save the :class:`~mongoengine.Document` to the database. If the
        document already exists, it will be updated, otherwise it will be
        created.

        :param force_insert: only try to create a new document, don't allow
            updates of existing documents.
        :param validate: validates the document; set to ``False`` to skip.
        :param clean: call the document clean method, requires `validate` to be
            True.
        :param write_concern: Extra keyword arguments are passed down to
            :meth:`~pymongo.collection.Collection.save` OR
            :meth:`~pymongo.collection.Collection.insert`
            which will be used as options for the resultant
            ``getLastError`` command.  For example,
            ``save(..., write_concern={w: 2, fsync: True}, ...)`` will
            wait until at least two servers have recorded the write and
            will force an fsync on the primary server.
        :param cascade: Sets the flag for cascading saves.  You can set a
            default by setting "cascade" in the document __meta__
        :param cascade_kwargs: (optional) kwargs dictionary to be passed throw
            to cascading saves.  Implies ``cascade=True``.
        :param _refs: A list of processed references used in cascading saves
        :param save_condition: only perform save if matching record in db
            satisfies condition(s) (e.g. version number).
            Raises :class:`OperationError` if the conditions are not satisfied
        :param signal_kwargs: (optional) kwargs dictionary to be passed to
            the signal calls.

        .. versionchanged:: 0.5
            In existing documents it only saves changed fields using
            set / unset.  Saves are cascaded and any
            :class:`~bson.dbref.DBRef` objects that have changes are
            saved as well.
        .. versionchanged:: 0.6
            Added cascading saves
        .. versionchanged:: 0.8
            Cascade saves are optional and default to False.  If you want
            fine grain control then you can turn off using document
            meta['cascade'] = True.  Also you can pass different kwargs to
            the cascade save using cascade_kwargs which overwrites the
            existing kwargs with custom values.
        .. versionchanged:: 0.8.5
            Optional save_condition that only overwrites existing documents
            if the condition is satisfied in the current db record.
        .. versionchanged:: 0.10
            :class:`OperationError` exception raised if save_condition fails.
        .. versionchanged:: 0.10.1
            :class: save_condition failure now raises a `SaveConditionError`
        .. versionchanged:: 0.10.7
            Add signal_kwargs argument
        """
        if item._meta.get('abstract'):
            raise mongoengine.InvalidDocumentError('Cannot save an abstract document.')

        signal_kwargs = signal_kwargs or {}
        mongoengine.signals.pre_save.send(item.__class__, document=item, **signal_kwargs)

        if validate:
            item.validate(clean=clean)

        if write_concern is None:
            write_concern = {'w': 1}

        doc = item.to_mongo()

        created = ('_id' not in doc or item._created or force_insert)

        mongoengine.signals.pre_save_post_validation.send(item.__class__, document=item,
                                              created=created, **signal_kwargs)
        # it might be refreshed by the pre_save_post_validation hook, e.g., for etag generation
        doc = item.to_mongo()

        if item._meta.get('auto_create_index', True):
            await self.mongo_model_ensure_indexes(item)

        try:
            # Save a new document or update an existing one
            if created:
                object_id = await self._mongo_save_create(item, doc, force_insert, write_concern)
            else:
                object_id, created = await self._mongo_save_update(item, doc, save_condition,
                                                                   write_concern
                                                                  )

            if cascade is None:
                cascade = (item._meta.get('cascade', False) or
                           cascade_kwargs is not None)

            if cascade:
                kwargs = {
                    'force_insert': force_insert,
                    'validate': validate,
                    'write_concern': write_concern,
                    'cascade': cascade
                }
                if cascade_kwargs:  # Allow granular control over cascades
                    kwargs.update(cascade_kwargs)
                kwargs['_refs'] = _refs
                await self.mongo_cascade_save(item, **kwargs)

        except pymongo.errors.DuplicateKeyError as err:
            message = 'Tried to save duplicate unique keys (%s)'
            raise mongoengine.NotUniqueError(message % six.text_type(err))
        except pymongo.errors.OperationFailure as err:
            message = 'Could not save document (%s)'
            if re.match('^E1100[01] duplicate key', six.text_type(err)):
                # E11000 - duplicate key error index
                # E11001 - duplicate key on update
                message = 'Tried to save duplicate unique keys (%s)'
                raise mongoengine.NotUniqueError(message % six.text_type(err))
            raise mongoengine.OperationError(message % six.text_type(err))

        # Make sure we store the PK on this document now that it's saved
        id_field = item._meta['id_field']
        if created or id_field not in item._meta.get('shard_key', []):
            item[id_field] = item._fields[id_field].to_python(object_id)

        mongoengine.signals.post_save.send(item.__class__, document=item,
                               created=created, **signal_kwargs)

        item._clear_changed_fields()
        item._created = False

        return item

    async def insert_mongo(self, model, values):
        """Supports Document, dict, or list(builk insert)

        :param mongoengine.Document|str model: The mongo schema or collection name.
        :param mongoengine.Document|dict|list values: the mongo document or dict or list value to be inserted.
        :return bool:
        """
        collection = self._prepare_mongo_collection(model)
        result = False
        if isinstance(values, mongoengine.Document):
            result = await self.save_mongo(values)
        elif isinstance(values, dict):
            result = await collection.insert_one(values)
        else:
            inserts = []
            for v in values:
                if isinstance(v, dict):
                    inserts.append(v)
                elif isinstance(v, mongoengine.Document):
                    item = v.to_mongo()
                    inserts.append(item)
                else:
                    raise Exception("insert mongodb values should either be dict or Document type!")
            if inserts:
                result = await collection.insert_many(inserts)
        return result

    async def update_mongo(self, model, item, condition):
        """
        update mongo model

        :param mongoengine.Document|str model: The mongo schema or collection name.
        :param dict item: update key and value.
        :param dict condition: update by this conditions.
        :return int: updated count.
        """
        if not (condition and isinstance(item, dict) and ("id" or "_id") not in item):
            raise mongoengine.OperationError("Invalid input.")
        collection = self._prepare_mongo_collection(model)

        try:
            updated_ret = await collection.update_many(condition, {"$set": item})
            updated_count = updated_ret.modified_count
        except Exception:
            updated_count = 0

        return updated_count

    async def del_item_mongo(self, item, condition=None):
        """
        :param mongoengine.Document|str item: The mongo document or schema or collection name
        :param dict|None condition: the delete condition if condition specified, the field 
            should be provided when item is schame or collection name.
        :return bool:
        """
        result = False
        collection = self._prepare_mongo_collection(item)
        if not condition:
            result = await collection.delete_one({'_id': item.pk})
        elif isinstance(condition, dict):
            result = await collection.delete_many(condition)
        return result

    def _prepare_mongo_collection(self, model):
        dbinst = self.get_mongo_dbinstance(model)
        if isinstance(model, str):
            collection_name = model
        else:
            collection_name = model._meta.get('collection')
            if not collection_name:
                collection_name = model._class_name
        collection = dbinst.conn[collection_name]
        return collection

    def _format_mongo_query(self, model, filters):
        q = mongoengine.queryset.QuerySet(model, None)
        qfilters = []
        kwfilters = {}
        if isinstance(filters, tuple):
            for f in filters:
                if isinstance(f, dict):
                    for k,v in f.items():
                        kwfilters[k] = v
                elif isinstance(f, list):
                    for v in f:
                        qfilters.append(v)
        elif isinstance(filters, dict):
            kwfilters = filters
        elif isinstance(filters, list):
            qfilters = filters

        if qfilters or kwfilters:
            q = q.filter(*qfilters, **kwfilters)
        elif filters:
            q = q.filter(filters)
        return q

    async def mongo_model_ensure_indexes(self, model):
        """Checks the document meta data and ensures all the indexes exist.

        Global defaults can be set in the meta - see :doc:`guide/defining-documents`

        .. note:: You can disable automatic index creation by setting
                  `auto_create_index` to False in the documents meta data
        """
        background = model._meta.get('index_background', False)
        drop_dups = model._meta.get('index_drop_dups', False)
        index_opts = model._meta.get('index_opts') or {}
        index_cls = model._meta.get('index_cls', True)

        collection = self._prepare_mongo_collection(model)
        # 746: when connection is via mongos, the read preference is not necessarily an indication that
        # this code runs on a secondary
        if not collection.is_mongos and collection.read_preference > 1:
            return

        # determine if an index which we are creating includes
        # _cls as its first field; if so, we can avoid creating
        # an extra index on _cls, as mongodb will use the existing
        # index to service queries against _cls
        cls_indexed = False

        # Ensure document-defined indexes are created
        if model._meta['index_specs']:
            index_spec = model._meta['index_specs']
            for spec in index_spec:
                spec = spec.copy()
                fields = spec.pop('fields')
                cls_indexed = cls_indexed or mongoengine.document.includes_cls(fields)
                opts = index_opts.copy()
                opts.update(spec)

                # we shouldn't pass 'cls' to the collection.ensureIndex options
                # because of https://jira.mongodb.org/browse/SERVER-769
                if 'cls' in opts:
                    del opts['cls']

                if mongoengine.pymongo_support.IS_PYMONGO_GTE_37:
                    collection.create_index(fields, background=background, **opts)
                else:
                    collection.ensure_index(fields, background=background,
                                            drop_dups=drop_dups, **opts)

        # If _cls is being used (for polymorphism), it needs an index,
        # only if another index doesn't begin with _cls
        if index_cls and not cls_indexed and model._meta.get('allow_inheritance'):

            # we shouldn't pass 'cls' to the collection.ensureIndex options
            # because of https://jira.mongodb.org/browse/SERVER-769
            if 'cls' in index_opts:
                del index_opts['cls']

            if mongoengine.pymongo_support.IS_PYMONGO_GTE_37:
                collection.create_index('_cls', background=background,
                                        **index_opts)
            else:
                collection.ensure_index('_cls', background=background,
                                        **index_opts)

    async def _mongo_save_create(self, item, doc, force_insert, write_concern):
        """Save a new document.

        Helper method, should only be used inside save().
        """
        collection = self._prepare_mongo_collection(item)
        if force_insert:
            insert_result = await collection.insert_one(doc)
            return insert_result.inserted_id
        # insert_one will provoke UniqueError alongside save does not
        # therefore, it need to catch and call replace_one.
        if '_id' in doc:
            raw_object = await collection.replace_one(
                {'_id': doc['_id']}, doc)
            if raw_object:
                return doc['_id']

        insert_result = await collection.insert_one(doc)
        object_id = insert_result.inserted_id

        # In PyMongo 3.0, the save() call calls internally the _update() call
        # but they forget to return the _id value passed back, therefore getting it back here
        # Correct behaviour in 2.X and in 3.0.1+ versions
        if not object_id and pymongo.version_tuple == (3, 0):
            pk_as_mongo_obj = item._fields.get(item._meta['id_field']).to_mongo(item.pk)
            rc = await self.find_one_mongo(item.__class__, pk=pk_as_mongo_obj)
            if rc:
                object_id = rc.pk
            # object_id = (
            #     item._qs.filter(pk=pk_as_mongo_obj).first() and
            #     item._qs.filter(pk=pk_as_mongo_obj).first().pk
            # )  # TODO doesn't this make 2 queries?

        return object_id

    async def _mongo_save_update(self, item, doc, save_condition, write_concern):
        """Update an existing document.

        Helper method, should only be used inside save().
        """
        collection = self._prepare_mongo_collection(item)
        object_id = doc['_id']
        created = False

        select_dict = {}
        if save_condition is not None:
            select_dict = mongoengine.queryset.query(item.__class__, **save_condition)
            # select_dict = mongoengine.transform.query(item.__class__, **save_condition)

        select_dict['_id'] = object_id

        # Need to add shard key to query, or you get an error
        shard_key = item._meta.get('shard_key', tuple())
        for k in shard_key:
            path = item._lookup_field(k.split('.'))
            actual_key = [p.db_field for p in path]
            val = doc
            for ak in actual_key:
                val = val[ak]
            select_dict['.'.join(actual_key)] = val

        update_doc = item._get_update_doc()
        if update_doc:
            wc = write_concern.pop('w')
            upsert = save_condition is None
            last_error = await collection.update_one(select_dict, update_doc,
                                                     upsert=upsert, **write_concern)
            if not upsert and last_error._UpdateResult__raw_result['n'] == 0:
                raise mongoengine.SaveConditionError('Race condition preventing'
                                         ' document update detected')
            if last_error is not None:
                updated_existing = last_error.raw_result.get('updatedExisting')
                if updated_existing is False:
                    created = True
                    # !!! This is bad, means we accidentally created a new,
                    # potentially corrupted document. See
                    # https://github.com/MongoEngine/mongoengine/issues/564

        return object_id, created

    async def mongo_cascade_save(self, item, doc, **kwargs):
        """Recursively save any references and generic references on the
        document.
        """
        _refs = kwargs.get('_refs') or []

        ReferenceField = mongoengine.document._import_class('ReferenceField')
        GenericReferenceField = mongoengine.document._import_class('GenericReferenceField')

        for name, cls in list(item._fields.items()):
            if not isinstance(cls, (ReferenceField,
                                    GenericReferenceField)):
                continue

            ref = item._data.get(name)
            if not ref or isinstance(ref, mongoengine.DBRef):
                continue

            if not getattr(ref, '_changed_fields', True):
                continue

            ref_id = "%s,%s" % (ref.__class__.__name__, str(ref._data))
            if ref and ref_id not in _refs:
                _refs.append(ref_id)
                kwargs["_refs"] = _refs
                await self.save_mongo(ref, **kwargs)
                ref._changed_fields = []

    ################ end part of mongodb operations ################