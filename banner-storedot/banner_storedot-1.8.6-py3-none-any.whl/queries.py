from re import split
from typing import Union, Dict
from numbers import Number
from threading import Thread
from functools import wraps, partial
from collections.abc import Iterable
from collections import ChainMap
from hashlib import md5

import MySQLdb as mysql
from MySQLdb.cursors import DictCursor
from MySQLdb._exceptions import OperationalError, ProgrammingError
import pandas as pd
import numpy as np
from joblib import Parallel, delayed

from banner.utils.const import (
    FIRST_NEWARE_DATA_TABLE, SECOND_NEWARE_DATA_TABLE, FIRST_NEWARE_AUX_TABLE, SECOND_NEWARE_AUX_TABLE, 
    NW_TEMP, CACHE_CONNECTION_KWARG, TTL_KWARG, NW_DATA_SIGNIFICANT_COLUMNS, NW_AUX_SIGNIFICANT_COLUMNS,
    NW_AUX_CHANNEL, NW_SEQ
)
from banner.utils.neware import calculate_neware_columns, calculate_dqdv, merge_cache, query_cache
from banner.utils.web2py import parse_w2p_to_mysql_query, COLUMN_TO_LABEL as W2P_COLUMN_TO_LABEL, LABEL_TO_COLUMN as W2P_LABEL_TO_COLUMN
from banner.utils.misc import is_non_string_iterable, to_sql_range
from banner.connection import Connection, Storage, RelationalConnection, MySqlConnection

class Queries(object):
    @staticmethod
    def CONNECTIONS(conns: Dict[str, Connection] = {}):
        ''' 
            Dict of pre existing Connection Objects (name: connection)
            Setup new connections, returns all available
        '''
        try:
            Queries.CONNECTIONS.__CONNECTIONS.update(conns)

        except AttributeError:
            Queries.CONNECTIONS.__CONNECTIONS = {**conns}

        if not Queries.CONNECTIONS.__CONNECTIONS:
            return {None: None}

        return Queries.CONNECTIONS.__CONNECTIONS

    @staticmethod
    def CACHE(con: Storage = None):
        ''' 
            Sets a Storage Connection as default Cache
        '''
        try:
            assert(Queries.CACHE.__CACHE_CONNECTION)

        except (AssertionError, AttributeError):
            Queries.CACHE.__CACHE_CONNECTION = None

        if isinstance(con, Storage):
            Queries.CACHE.__CACHE_CONNECTION = con
        
        return Queries.CACHE.__CACHE_CONNECTION

    @staticmethod
    def __get_known_connection(connection: Union[Connection, str], typ: type = Connection):
        # If no connection is provided, grab first available
        if not connection:
            connections = [
                _connection for _connection in Queries.CONNECTIONS().values() if isinstance(_connection, typ)
            ]

            if not connections:
                raise IndexError('No Connections could be found')

            connection = connections[0]

        # Provided connection is not a Connection, is it a key?
        if not isinstance(connection, Connection):
            connection = Queries.CONNECTIONS().get(str(connection), connection)
        
        # No connection could be found
        if not isinstance(connection, Connection):
            raise KeyError(f'Unknown Connection', connection)

        if not isinstance(connection, typ):
            raise TypeError('Wrong Connection type', connection)

        return connection

    def __digested_key(func: callable, *args, **kwargs):
        key = f'{func.__name__}-{"_".join(str(arg) for arg in args).strip()}'

        if kwargs:
            _kwargs = "_".join(
                [f'{key}:{str(value).strip()}' for key, value in kwargs.items() if type(value) not in (pd.DataFrame, )]
            )
            key += f'-{_kwargs}'

        if len(key) > 300:
            key = md5(key.encode('utf-8')).hexdigest()
        
        return key

    def __cache_query(key, value, cache: Storage, ttl=None):
        try:
            assert(isinstance(cache, Storage))
            
            return cache.store(
                key, 
                value, 
                ttl=ttl, 
                nx=True
            )

        except AssertionError:
            pass
        
        except Exception as e:
            print(f'Failed Caching {key} into {cache}', e)
    
    def __cached_query(key, cache: Storage):
        try:
            assert(isinstance(cache, Storage))
            
            cached = cache.retrieve(
                key, resp_type=pd.DataFrame
            )
            
            assert(isinstance(cached, pd.DataFrame))

            return cached

        except AssertionError:
            return pd.DataFrame()

    def __cache(func):
        @wraps(func)
        def inner(*args, **kwargs):
            cache = kwargs.get(CACHE_CONNECTION_KWARG, None)

            if cache is None: # Specifically checking for None, If False Do not cache!
                cache = Queries.CACHE()
            
            ttl = kwargs.get(TTL_KWARG, None)
            
            key = Queries.__digested_key(inner, *args, **kwargs)
            
            response = Queries.__cached_query(key, cache)
            
            if not response.empty:
                return response
            
            response = func(*args, **kwargs)
            
            # Cache TODO USE CELERY
            Thread(
                target=Queries.__cache_query, 
                kwargs=dict(
                    key=key,
                    value=response,
                    cache=cache,
                    ttl=ttl
                )
            ).start()

            return response

        return inner

    @staticmethod
    def __query(query: str, connection=None, cache=None, ttl=None, w2p_parse=True) -> pd.DataFrame:
        if not isinstance(query, str):
            return pd.DataFrame()

        connection = Queries.__get_known_connection(connection)
        
        if w2p_parse:
            query = parse_w2p_to_mysql_query(query)
        #TODO CHANGE TO LABELS?! NEEDS TO KNOW RAW
        return connection.retrieve(query)
    
    @staticmethod
    @__cache
    def simple_query(query: str, connection: Union[Connection, str] = None, cache: Storage = None, ttl: int = None, w2p_parse: bool = True) -> pd.DataFrame:
        '''
            Queries a given Connection/str of a known connection (or first known) return result as DataFrame
            Cache if cache or first known with ttl or default ttl for cache
            Raises KeyError and OperationalError
        '''
        return Queries.__query(
            query, 
            connection=connection, 
            cache=cache, 
            ttl=ttl, 
            w2p_parse=w2p_parse
        )

    @staticmethod
    def describe_table(table: str, connection: Union[RelationalConnection, str] = None) -> pd.DataFrame:
        '''
            Describes a table in connection
            Raises OperationalError and KeyError(Failed to find a connection for given key) 
        '''
        if not isinstance(table, str):
            return pd.DataFrame()

        connection = Queries.__get_known_connection(connection, RelationalConnection)
        
        data = connection.describe(table)
        
        data.insert(0, "Label", data['Field'].map(W2P_COLUMN_TO_LABEL))

        return data

    @staticmethod
    def describe(connection: Union[RelationalConnection, str] = None) -> pd.DataFrame:
        '''
            Describe Table names in connection
            Raises OperationalError and KeyError(Failed to find a connection for given key) 
        '''
        
        return Queries.__get_known_connection(connection, RelationalConnection).describe()

    @staticmethod
    @__cache
    def table_query(
        table: str, columns: Union[list, str] = '*', condition: str = 'TRUE', 
        connection: Union[RelationalConnection, str] = None, raw: bool = False,
        cache: Storage=None, ttl: bool = None
    ) -> pd.DataFrame:
        '''
            Queries a given connection for 'SELECT {columns} FROM {table} WHERE {condition}'
            Accepts both column values and labels
            raw=True - column names as in db
            Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
            Cache if cache or first known with ttl or default ttl for cache
            Raises OperationalError and KeyError(Failed to find a connection for given key) 
        '''
        if isinstance(columns, str):
            columns = list(
                map(
                    str.strip,
                    filter(
                        None, 
                        split(
                            ' , |, | ,|,',
                            columns
                        )
                    )
                )
            )
        
        _columns = [W2P_LABEL_TO_COLUMN.get(column, column) for column in columns]
        
        data = Queries.__query(
            f"SELECT {', '.join(_columns)} FROM {table} WHERE {condition}",
            connection=connection,
            cache=cache,
            ttl=ttl
        )
        
        if not raw:
            try:
                #Columns as requested!
                data.columns = columns 

            except ValueError:
                # Case columns contain *
                data.columns = [W2P_COLUMN_TO_LABEL.get(column, column) for column in data.columns]
                pass
            

        return data

    @staticmethod
    @__cache
    def form_factor_query(
        table: str, experiments=[], templates=[], cells=[], tests=[],
        columns: Union[list, str] = '*', condition: str = 'TRUE', 
        connection: Union[RelationalConnection, str] = None, raw: bool = False,
        cache: Storage=None, ttl: bool = None
    ) -> pd.DataFrame:
        '''
            Queries a given connection for 'SELECT {table}, {table}_test, {table}_test_template FROM {table} WHERE {condition}'
            Accepts both column values and labels
            raw=True - column names as in db
            Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
            Cache if cache or first known with ttl or default ttl for cache
            Raises OperationalError and KeyError(Failed to find a connection for given key) 
        '''
        if isinstance(columns, str):
            columns = list(
                map(
                    str.strip,
                    filter(
                        None, 
                        split(
                            ' , |, | ,|,',
                            columns
                        )
                    )
                )
            )
        
        _columns = ', '.join(
            [W2P_LABEL_TO_COLUMN.get(column, column) for column in columns]
        )
        
        _columns = f'{table}.*, {table}_test.*, {table}_test_template.*' if _columns == '*' else _columns
        
        __condition = condition
    
        if experiments:
            __condition += f' AND {table}.experiments REGEXP "{"|".join([str(ex) for ex in experiments])}"'
            
        if templates:
            __condition += f' AND {table}_test_template.id IN ({",".join([str(tmp) for tmp in templates])})'
            
        if cells:
            __condition += f' AND {table}.id IN ({",".join([str(cell) for cell in cells])})'
            
        if tests:
            __condition += f' AND {table}_test.id IN ({",".join([str(test) for test in tests])})'
            
        data = Queries.__query(
            f"""
                SELECT {_columns}
                FROM {table}
                LEFT JOIN {table}_test
                ON {table}.id = {table}_test.{table}_id
                LEFT JOIN {table}_test_template
                ON {table}_test.test_type_id = {table}_test_template.id
                WHERE {__condition}
            """,
            connection=connection,
            cache=cache,
            ttl=ttl
        )
        
        if not raw:
            try:
                #Columns as requested!
                data.columns = columns 

            except ValueError:
                # Case columns contain *
                data.columns = [W2P_COLUMN_TO_LABEL.get(column, column) for column in data.columns]
                pass
            
        return data

    @staticmethod
    @__cache
    def neware_query(
        device: int, unit: int, channel: int, test: int, connection: Union[MySqlConnection, str] = None, 
        raw: bool = False, dqdv: bool = False, columns: Union[list, str] = '*', condition: str = 'TRUE', 
        temperature: bool = True, cache_data: pd.DataFrame = pd.DataFrame(), cache: Storage = None, ttl: int = None,
    ) -> pd.DataFrame:
        '''
            Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
            Cache if cache or first known with ttl or default ttl for cache
            If dqdv -> neware.calc_dq_dv
            Raises KeyError and OperationalError
        '''
        connection = Queries.__get_known_connection(connection, MySqlConnection)
        
        # Look for the tables
        try:
            neware_data = Queries.__query(
                f'SELECT * FROM h_test WHERE dev_uid = {device} AND unit_id = {unit} AND chl_id = {channel} AND test_id = {test}',
                connection=connection
            ).iloc[0] # A single row is returned since we looked by primary key

        except IndexError:
            raise TypeError(f'{connection.name} has No data for device:{device}, unit:{unit}, channel:{channel}') 
        
        # Select only significant columns
        __data_columns = NW_DATA_SIGNIFICANT_COLUMNS

        if columns != '*':
            if isinstance(columns, str):
                columns = list(
                    map(
                        str.strip,
                        filter(
                            None, 
                            split(
                                ' , |, | ,|,',
                                columns
                            )
                        )
                    )
                )

            __data_columns = list((set(columns) & set(__data_columns)) | set([NW_SEQ]))
            
        __data_columns, __aux_columns = ', '.join(__data_columns), ', '.join(NW_AUX_SIGNIFICANT_COLUMNS)
        
        # Parse W2P query
        condition = parse_w2p_to_mysql_query(condition)
        
        # Try to adjust query!
        if isinstance(cache_data, pd.DataFrame) and not cache_data.empty and condition != '1':
            condition = query_cache(
                cache_data, condition
            )
        
        # Init data(main neware data), aux_data(temp data)
        data, aux_data = pd.DataFrame(), pd.DataFrame()

        if __data_columns:
            data = pd.concat([
                Queries.__query(
                    f'SELECT {__data_columns} FROM {neware_data[FIRST_NEWARE_DATA_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test} AND {condition}', 
                    connection=connection
                ) if neware_data[FIRST_NEWARE_DATA_TABLE] else pd.DataFrame(),
                Queries.__query(
                    f'SELECT {__data_columns} FROM {neware_data[SECOND_NEWARE_DATA_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test} AND {condition}', 
                    connection=connection
                ) if neware_data[SECOND_NEWARE_DATA_TABLE] else pd.DataFrame()
            ], ignore_index=True)
        
        if temperature:
            aux_data = pd.concat([
                Queries.__query(
                    f'SELECT {__aux_columns} FROM {neware_data[FIRST_NEWARE_AUX_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test} AND {condition}', 
                    connection=connection
                ) if neware_data[FIRST_NEWARE_AUX_TABLE] else pd.DataFrame(),
                Queries.__query(
                    f'SELECT {__aux_columns} FROM {neware_data[SECOND_NEWARE_AUX_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test} AND {condition}', 
                    connection=connection
                ) if neware_data[SECOND_NEWARE_AUX_TABLE] else pd.DataFrame()
            ], ignore_index=True)
            
        __data_columns, __aux_columns = list(data.columns), list(aux_data.columns) #Response columns
        
        try:
            data = pd.merge(data[__data_columns], aux_data.group_by_auxchl(), on=NW_SEQ) # Merge
            
        except (ValueError, KeyError):
            pass
        
        if not raw:
            try:
                data = calculate_neware_columns(data, cache_df=cache_data) # Calculate neware columns
                
            except KeyError:
                pass

            try:
                data = merge_cache(data, cache_data) # Merge provided cache data
                    
            except (TypeError, KeyError):
                pass

        if dqdv:
            try:
                data['dqdv'] = calculate_dqdv(data, raw=raw) # Calculate dqdv
                
            except KeyError:
                pass

        if columns != '*':
            try:
                data = data[columns]

            except KeyError:
                pass

        return data

    @staticmethod
    def __neware_queries(
        devices: list, units: list, channels: list, tests: list, connection: Union[MySqlConnection, str] = None, 
        cache: Storage = None, ttl: int = None, raw: bool = False, dqdv: bool = False, 
        columns: Union[list, str] = '*', condition: str = 'TRUE',  
        temperature: bool = True, cache_data: pd.DataFrame = pd.DataFrame()
    ):  
        _connection_key = connection

        if isinstance(connection, Connection):
            _connection_key = str(name)

        data = dict()
        
        for device, unit, channel, test in zip(devices, units, channels, tests):
            data.update({
                tuple([_connection_key, device, unit, channel, test]): Queries.neware_query(
                    device, unit, channel, test,
                    connection=connection,
                    cache=cache,
                    ttl=ttl,
                    raw=raw, 
                    dqdv=dqdv, 
                    condition=condition,
                    columns=columns,
                    temperature=temperature, 
                    cache_data=cache_data[
                        (cache_data.dev_uid == int(device)) &
                        (cache_data.unit_id == int(unit)) & 
                        (cache_data.chl_id == int(channel)) & 
                        (cache_data.test_id == int(test))
                    ]
                )
            })
        
        return data

    @staticmethod
    @__cache
    def neware_cache_query(
        ips: Union[list, Number], devices: Union[list, Number], units: Union[list, Number], 
        channels: Union[list, Number], tests: Union[list, Number], columns: Union[list, str] = '*', 
        condition: str = 'TRUE', connection: Union[MySqlConnection, str] = None, 
        cache: Storage = None, ttl: int = None
    ) -> pd.DataFrame:
        '''
            Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
            Cache if cache or first known with ttl or default ttl for cache
            Raises KeyError and OperationalError
        '''
        connection = Queries.__get_known_connection(connection, MySqlConnection)

        multiple = False

        if any(is_non_string_iterable(arg) for arg in [ips, devices, units, channels, tests]):
            multiple = True

        if not isinstance(columns, str):
            columns = ','.join(columns)
        
        keys = [
            f'({ip},{device},{unit},{channel},{test})' for ip, device, unit, channel, test in zip(ips, devices, units, channels, tests)
        ]

        keys = f'(ip,dev_uid,unit_id,chl_id,test_id) IN ({",".join(keys)})'
        
        cache_data = pd.DataFrame()
        
        for cache_table in ('neware_cache', 'neware_pulses_cache', 'neware_cache_anode'):
            cache_data = pd.concat([
                cache_data,
                Queries.__query(f"""
                        SELECT {columns} FROM {cache_table} 
                        WHERE {keys}
                        AND {condition}
                    """,
                    connection=connection
                )
            ])
            
            if not multiple and not cache_data.empty:
                return cache_data
        
        return cache_data

    @staticmethod
    def __neware_tests_query(
        table: str, experiments: str = '', templates: str = '', tests: str = '', cells: str = '', 
        columns: Union[list, str] = '*', condition: str = 'TRUE', raw: bool = False, dqdv: bool = False, 
        temperature: bool = True, connection: Union[MySqlConnection, str] = None, cache: Storage = None, ttl: int = None
    ):  
        if not any([experiments, templates, tests, cells]):
            raise ValueError('A combination of experiments, templates, tests, cells is Required')
        
        connection = Queries.__get_known_connection(connection, MySqlConnection)

        __tests_query = f"""
            SELECT 
                {table}.id, {table}_test.ip, {table}_test.device, {table}_test.unit, {table}_test.channel, {table}_test.test_id
            FROM {table}
            LEFT JOIN {table}_test
            ON {table}.id = {table}_test.{table}_id
            LEFT JOIN {table}_test_template
            ON {table}_test.test_type_id = {table}_test_template.id
            WHERE 1
        """

        if experiments and isinstance(experiments, str):
            __tests_query += f' AND {experiments}'
        
        if templates and isinstance(templates, str):
            __tests_query += f' AND {templates}'

        if tests and isinstance(tests, str):
            __tests_query += f' AND {tests}'

        if cells and isinstance(cells, str):
            __tests_query += f' AND {cells}'
        
        __tests = Queries.__query(
            __tests_query,
            connection=connection,
            cache=cache,
            ttl=ttl
        ).dropna()
        
        if __tests.empty:
            return {}

        # Make sure all data is numeric
        __tests = __tests.astype(int, errors='ignore')
        
        __cached_data = Queries.neware_cache_query(
            __tests['ip'].to_list(),
            __tests['device'].to_list(),
            __tests['unit'].to_list(),
            __tests['channel'].to_list(),
            __tests['test_id'].to_list(),
            connection=connection,
            cache=cache,
            ttl=ttl
        )
        
        __tests_by_ip = __tests.groupby('ip')
        
        data = Parallel(n_jobs=__tests_by_ip.ngroups, require='sharedmem', verbose=0)(
            delayed(Queries.__neware_queries)(
                df['device'].values, df['unit'].values, df['channel'].values, df['test_id'].values,
                connection=name, cache=cache, ttl=ttl, raw=raw, columns=columns,
                dqdv=dqdv, condition=condition, temperature=temperature,
                cache_data=__cached_data[__cached_data.ip == int(name)]
            )
            for name, df in __tests_by_ip
        )
        
        return dict(ChainMap(*data))

    @staticmethod
    def neware_tests_query(
        table: str, experiments: Union[list, Number, str] = [], templates: Union[list, Number, str] = [], 
        tests: Union[list, Number, str] = [], cells: Union[list, Number, str] = [], columns: Union[list, str] = '*', 
        condition: str = 'cycle < 2', raw: bool = False, dqdv: bool = False, temperature: bool = True,
        connection: Union[MySqlConnection, str] = None, cache: Storage = None, ttl: int = None
    ):
        if not any([experiments, templates, tests, cells]):
            raise ValueError('A combination of experiments, templates, tests, cells is Required')
        
        if experiments and not isinstance(experiments, str):
            experiments = to_sql_range(experiments, 'experiments', table, 'REGEXP')

        if templates and not isinstance(templates, str):
            templates = to_sql_range(templates, 'id', f'{table}_test_template')

        if tests and not isinstance(tests, str):
            tests = to_sql_range(tests, 'id', f'{table}_test')

        if cells and not isinstance(cells, str):
            cells = to_sql_range(cells, 'id', table)
        
        return Queries.__neware_tests_query(
            table, experiments, templates, 
            tests, cells, columns, condition, raw, 
            dqdv, temperature, connection, cache, ttl
        )

    
    




