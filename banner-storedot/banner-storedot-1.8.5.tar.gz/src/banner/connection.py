
from typing import Union, Dict, Iterable
from abc import ABC, abstractmethod
from enum import Enum
from sys import getsizeof
from json import loads
from itertools import chain
from re import fullmatch

from MySQLdb import connect as mysql_connect, MySQLError
from MySQLdb._exceptions import OperationalError
from MySQLdb.cursors import DictCursor

from psycopg2 import connect as postgres_sql_connect, Error as PostgresSQLError
from psycopg2.extras import RealDictCursor
from psycopg2.errors import DatabaseError as PostgresSQLDatabaseError
import redis
from pandas import DataFrame

class ConnectionType(Enum):
    mysql = 'mysql'
    redis = 'redis'
    postgres = 'postgres'

class ConnectionFactory(object):
    ''' Connection Factory'''
    def __new__(self, con_type: Union[ConnectionType, str] = ConnectionType.mysql, **kwargs):
        try:
            con_type = ConnectionType[con_type]

        except KeyError:
            pass
            
        if not isinstance(con_type, ConnectionType):
            raise TypeError('Unknown Connection Type')
        
        if con_type is ConnectionType.redis:
            return RedisConnection(**kwargs)
            
        return MySqlConnection(**kwargs)        

class Connection(ABC):
    @abstractmethod
    def retrieve(self, query: str):
        pass

class RelationalConnection(Connection):
    @abstractmethod
    def describe(self, table: str = ''):
        pass

class Storage(Connection):
    @abstractmethod
    def store(self, key, value):
        pass

    @abstractmethod
    def keys(self, query):
        pass

class PrintableConnection(Connection):
    @abstractmethod
    def name(self):
        pass
    
    @abstractmethod
    def __str__(self):
        pass

class RedisConnection(Storage, PrintableConnection):
    HOUR = 3600
    ENTRY_SIZE_LIMIT = 64000000
    DATAFRAME_ENTRY_LIMIT = 300000
    CHUNK_PREFIX = '#'
    TTL_KEY = 'ttl'

    def __init__(self, host, port=6379, passwd=None, db=0, ssl_key=None, ssl_cert=None, name=None, ttl=HOUR):
        self.data = dict(
            host=host,
            port=port,
            password=passwd,
            db=db,
            ssl_keyfile=ssl_key,
            ssl_certfile=ssl_cert,
        )

        self.__ttl = ttl or RedisConnection.HOUR
        self.__name = name

        # Redis manages opening/closing by itself, it is safe to init it here
        self.instance = redis.Redis(
            **self.data, 
            decode_responses=True
        )
    
    def keys(self, query: str):
        '''
            Retrieve Keys from Storage
        '''
        return self.instance.keys(pattern=f'{str(query)}')

    def retrieve(self, query: str, resp_type=None):
        '''
            Retrieve Values from Storage
        '''
        # Look for all possible Keys
        _keys = self.keys(f'{query}*')
        _keys = sorted(
            [key for key in _keys if fullmatch(r'(%s)(%s[0-9]+)?' % (query, RedisConnection.CHUNK_PREFIX), key)]
        ) # Either fullmatch or contains additional #[0-9]+
        
        # Look for values
        # func = self.instance.get if isinstance(query, str) else self.instance.mget
        # values = func(query)
        values = self.instance.mget(_keys)
        
        # Parse by resp_type and return
        return self.__parse_result(values, resp_type)
    
    def __parse_result(self, result, _type=None):
        # Result could be a list or single value
        # Currently only handles DataFrame
        if _type == DataFrame:
            if isinstance(result, list):
                return DataFrame.from_dict(chain(*[loads(res) for res in result]), orient='columns')
        
            return DataFrame.from_dict(loads(result), orient='columns')

        return result
        
    def store(self, key, value, ttl=None, nx=False):
        ttl = ttl if isinstance(ttl, int) else self.__ttl
        
        # Case Pandas.DataFrame
        if isinstance(value, DataFrame):
            return self.__store_df(key, value, ttl, nx)

        return self.instance.set(key, value, ex=ttl, nx=nx)

    def __store_df(self, key, df, ttl, nx):
        if len(df) <= RedisConnection.DATAFRAME_ENTRY_LIMIT:
            return self.instance.set(key, df.to_json(orient='records'), ex=ttl, nx=nx)

        for index, chunck in enumerate(df.split(size=RedisConnection.DATAFRAME_ENTRY_LIMIT)): # Decorated function splitting df into list of dfs of size rows
            resp = self.instance.set(
                key + f'{RedisConnection.CHUNK_PREFIX}{index}' if index else key, 
                chunck.to_json(orient='records'), ex=ttl, nx=nx
            )
            
            if not resp:
                raise redis.ResponseError
        
        return True #All returned values are Truthy
        
    @property
    def name(self):
        return self.__name or str(self.data)

    def __str__(self):
        return self.name
            
class MySqlConnection(RelationalConnection, PrintableConnection):
    def __init__(self, host, user, passwd=None, db=None, ssl_key=None, ssl_cert=None, charset='utf8', use_unicode=True, name=None):
        self.data = dict(
            host=host,
            user=user,
            passwd=passwd,
            db=db,
            ssl=dict(key=ssl_key, cert=ssl_cert),
            charset=charset,
            use_unicode=use_unicode,
            cursorclass=DictCursor
        )

        self.__name = name

    def retrieve(self, query: str):
        try:
            instance = self.__connect()
            
            cursor = instance.cursor()
            
            cursor.execute(query)

            records = cursor.fetchall()

            cursor.close()
        
            records = DataFrame(records)
        
        except MySQLError as e:
            raise e
        
        finally:
            self.__close(instance)        

        return records

    def describe(self, table: str = ''):
        _query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{self.data.get('db')}'"

        if table:
            _query = f'DESCRIBE {table}'

        return self.retrieve(_query)

    def __connect(self):
        try:
            return mysql_connect(**self.data)

        except OperationalError:
            raise MySQLError(
                f'Connection to {self.name} Failed'
            )
      
    def __close(self, instance):
        try:
            instance.close() 
            
        except (AttributeError, MySQLError):
            pass
    
    @property
    def name(self):
        return self.__name or str(self.data)

    def __str__(self):
        return self.name

class PostgresSqlConnection(RelationalConnection, PrintableConnection):
    def __init__(self, host, user, port=5432, passwd=None, db=None, ssl_key=None, ssl_cert=None, charset='utf8', name=None):
        self.data = dict(
            host=host,
            user=user,
            password=passwd,
            dbname=db,
            sslkey=ssl_key,
            sslcert=ssl_cert
        )

        self.__name = name
        self.__charset = charset
        
    def retrieve(self, query: str):
        try:
            instance = self.__connect()
            
            cursor = instance.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(query)
            
            records = cursor.fetchall()
            
            cursor.close()
        
            records = DataFrame(records)

        except PostgresSQLError as e:
            raise e
        
        finally:
            self.__close(instance)        

        return records

    def describe(self, table: str = ''):
        _query = f"SELECT table_name FROM information_schema.tables"

        if table:
            _query = (
                'SELECT column_name as "Field", data_type as "Type", is_nullable as "Null", column_default as "Default"'
                f" FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{table}'"
            )
            
        return self.retrieve(_query)
    
    def __connect(self):
        try:
            instance = postgres_sql_connect(**self.data)
            instance.set_client_encoding(self.__charset)

            return instance

        except PostgresSQLError:
            raise PostgresSQLDatabaseError(
                f'Connection to {self.name} Failed'
            )
      
    def __close(self, instance):
        try:
            instance.close() 
            
        except (AttributeError, PostgresSQLError):
            pass

    @property
    def name(self):
        return self.__name or str(self.data)

    def __str__(self):
        return self.name