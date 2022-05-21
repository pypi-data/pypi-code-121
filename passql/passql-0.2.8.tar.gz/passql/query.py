from passql.exceptions import QueryException
from passql.interfaces import *
from passql.models import DbEntity
from passql.sql import Sql, SqlMaker
from typing import Union, Any, List, Type, TypeVar, Optional, Coroutine, Tuple, Set, Dict

__all__ = (
    'DbConnection',
)

TEntity = TypeVar('TEntity', bound=DbEntity)
TScalar = TypeVar('TScalar')
TVal = TypeVar('TVal', bound=Union[Any, Tuple])


class DbConnection:
    __slots__ = ('_connection', '_sql_maker')

    def __init__(self, origin_connection: IOriginConnection, sql_maker: SqlMaker):
        self._connection = origin_connection
        self._sql_maker = sql_maker

    @property
    def origin_connection(self) -> IOriginConnection:
        """ Connection received in constructor. """
        return self._connection

    def transaction(self) -> IOriginTransaction:
        """ Get transaction object. """
        return self._connection.transaction()

    def execute(self,
                sql: Union[Sql, str],
                params: Any = None,
                timeout: int = None) -> Coroutine[Any, Any, None]:
        """ Execute sql.

        :param sql: Query string or prepared Sql object.
        :param params: Parameters to parse to sql.
        :param timeout: Time limit for the operation.
        """

        if type(sql) is str and params is not None:
            sql = self._sql_maker(sql).format(params)
        else:
            sql = sql.format(params)

        try:
            return self._connection.execute(sql, timeout=timeout)
        except Exception as e:
            raise QueryException(sql, str(e))

    async def query_scalar(self,
                           t: Type[TScalar],
                           sql: Union[Sql, str],
                           params: Any = None,
                           timeout: int = None) -> Optional[TScalar]:
        """ Query single value.

        :param t: Return scalar type, only for generic.
        :param sql: Query string or prepared Sql object.
        :param params: Parameters to parse to sql.
        :param timeout: Time limit for the operation.
        :return: Value or None.
        """

        if type(sql) is str and params is not None:
            sql = self._sql_maker(sql).format(params)
        else:
            sql = sql.format(params)

        try:
            return await self._connection.fetchval(sql, timeout=timeout)
        except Exception as e:
            raise QueryException(sql, str(e))

    async def query_list(self,
                         t: Type[TEntity],
                         sql: Union[Sql, str],
                         params: Any = None,
                         timeout: int = None) -> List[TEntity]:
        """ Query list of entities.

        :param t: Return entity type.
        :param sql: Query string or prepared Sql object.
        :param params: Parameters to parse to sql.
        :param timeout: Time limit for the operation.
        :return: List of parsed entities.
        """

        if type(sql) is str and params is not None:
            sql = self._sql_maker(sql).format(params)
        else:
            sql = sql.format(params)

        try:
            result = await self._connection.fetch(sql, timeout=timeout)
        except Exception as e:
            raise QueryException(sql, str(e))

        for i in range(len(result)):
            result[i] = t.from_record(result[i])

        # noinspection PyTypeChecker
        return result

    async def query_values_list(self,
                                t: Type[TVal],
                                sql: Union[Sql, str],
                                params: Any = None,
                                timeout: int = None) -> List[TVal]:
        """ Query list of entities.

        :param t: Return tuple/scalar type of values, only for generic.
        :param sql: Query string or prepared Sql object.
        :param params: Parameters to parse to sql.
        :param timeout: Time limit for the operation.
        :return: List of objects.
        """

        if type(sql) is str and params is not None:
            sql = self._sql_maker(sql).format(params)
        else:
            sql = sql.format(params)

        try:
            result = await self._connection.fetch(sql, timeout=timeout)
        except Exception as e:
            raise QueryException(sql, str(e))

        if result:
            if len(result[0]) > 1:
                for i in range(len(result)):
                    # noinspection PyTypeChecker
                    result[i] = tuple(result[i].values())
            else:
                for i in range(len(result)):
                    # noinspection PyTypeChecker
                    result[i] = next(result[i].values())

        return result

    async def query_values_set(self,
                               t: Type[TVal],
                               sql: Union[Sql, str],
                               params: Any = None,
                               timeout: int = None) -> Set[TVal]:
        """ Query set of entities.

        :param t: Return tuple/scalar type of values, only for generic.
        :param sql: Query string or prepared Sql object.
        :param params: Parameters to parse to sql.
        :param timeout: Time limit for the operation.
        :return: Set of objects.
        """

        if type(sql) is str and params is not None:
            sql = self._sql_maker(sql).format(params)
        else:
            sql = sql.format(params)

        try:
            result = await self._connection.fetch(sql, timeout=timeout)
        except Exception as e:
            raise QueryException(sql, str(e))

        result_set = set()
        if result:
            if len(result[0]) > 1:
                for i in range(len(result)):
                    result_set.add(tuple(result[i].values()))
            else:
                for i in range(len(result)):
                    result_set.add(next(result[i].values()))

        return result_set

    async def query_values_dict(self,
                                key: str,
                                t_key: Type[TScalar],
                                t_value: Type[TVal],
                                sql: Union[Sql, str],
                                params: Any = None,
                                timeout: int = None) -> Dict[TScalar, TVal]:
        """ Query dictionary of entities.

        :param key: Name of returning column that will be the key of result dictionary.
        :param t_key: Return scalar type of key column, only for generic.
        :param t_value: Return tuple/scalar type of values, only for generic.
        :param sql: Query string or prepared Sql object.
        :param params: Parameters to parse to sql.
        :param timeout: Time limit for the operation.
        :return: Dictionary of objects by their keys.
        """

        if type(sql) is str and params is not None:
            sql = self._sql_maker(sql).format(params)
        else:
            sql = sql.format(params)

        try:
            result = await self._connection.fetch(sql, timeout=timeout)
        except Exception as e:
            raise QueryException(sql, str(e))

        result_dict = dict()
        if result:
            if len(result[0]) > 1:
                for i in range(len(result)):
                    result_dict[result[i][key]] = tuple(result[i].values())
            else:
                for i in range(len(result)):
                    result_dict[result[i][key]] = next(result[i].values())

        return result_dict

    async def query_first(self,
                          t: Type[TEntity],
                          sql: Union[Sql, str],
                          params: Any = None,
                          timeout: int = None) -> Optional[TEntity]:
        """ Query first entity.

        :param t: Return entity type.
        :param sql: Query string or prepared Sql object.
        :param params: Parameters to parse to sql.
        :param timeout: Time limit for the operation.
        :return: Entity parsed from first result row.
        """

        if type(sql) is str and params is not None:
            sql = self._sql_maker(sql).format(params)
        else:
            sql = sql.format(params)

        try:
            result = await self._connection.fetchrow(sql, timeout=timeout)
        except Exception as e:
            raise QueryException(sql, str(e))

        return None if result is None else t.from_record(result)

    async def close(self):
        """ Close connection. """
        await self._connection.close()

    def is_closed(self) -> bool:
        """ Is connection closed. """
        return self._connection.is_closed()
