import re
from collections import (
    Mapping,
)
from typing import (
    Any,
    NewType,
    Optional,
    Union,
)

import asyncpg
from django.apps import (
    apps,
)
from django.db import (
    DEFAULT_DB_ALIAS,
    connections as django_connections,
)
from django.db.models import (
    Field,
    Model,
)


ConnectionAlias = NewType('ConnectionAlias', str)
ConnectionInterface = Union[asyncpg.Pool, asyncpg.Connection]


connections: Mapping[ConnectionAlias, asyncpg.Pool] = {}


async def _make_connection(alias: ConnectionAlias) -> asyncpg.Pool:
    """
    Создаёт пул подключений asyncpg.Pool с теми же параметрами, что
    используются для создания подключения alias в django.
    Для внутреннего использования, используйте публичные интерфейсы
    get_pool и get_connection

    Args:
        alias: псевдоним БД в django

    Returns:
        пул подключений asyncpg.Pool

    """
    dj_connection = django_connections[alias]
    params = dj_connection.get_connection_params()
    return await asyncpg.create_pool(**params)


async def get_pool(alias: Optional[ConnectionAlias] = None) -> asyncpg.Pool:
    """
    Получение пула подключений asyncpg.Pool, аналогичного подключению
    alias в django

    Args:
        alias: псевдоним БД в django,
            если не передан - используется БД по-умолчанию

    Returns:
        пул подключений asyncpg.Pool

    """
    if alias is None:
        alias = DEFAULT_DB_ALIAS

    if alias not in connections:
        connections[alias] = await _make_connection(alias)

    connection = connections[alias]

    return connection


async def get_connection(alias: Optional[ConnectionAlias] = None) -> asyncpg.Connection:
    """
    Получение подключения asyncpg.Connection, аналогичного подключению
    alias в django

    Args:
        alias: псевдоним БД в django,
            если не передан - используется БД по-умолчанию

    Returns:
        подключение asyncpg.Connection

    """
    pool = await get_pool(alias)
    return pool.acquire()


async def truncate_table(conn: ConnectionInterface, model: Model):
    """
    Сброс данных из таблицы модели model

    Args:
        conn: asyncpg подключение к БД (asyncpg.Connection, либо asyncpg.Pool)
        model: django-модель

    """
    db_table = model._meta.db_table
    query = f'TRUNCATE TABLE {db_table} RESTART IDENTITY CASCADE'
    await conn.execute(query)


def get_unique_violation_details(
    exc: asyncpg.exceptions.UniqueViolationError,
) -> tuple[Model, Field, Any]:
    """
    Получение подробностей исключения UniqueViolationError

    Args:
        exc: исключение UniqueViolationError

    Returns:
        кортеж из django-модели, поля и значения, из-за которых произошла ошибка

    """

    # re.search без re.compile(pattern)
    # в сравнении с re.fullmatch по полному тексту сообшения и/или
    # с использованием прекомпилированного за пределами функции паттерна
    # работает быстрее всего в данном случае
    match = re.search(r'\((?P<column>.+)\)=\((?P<value>.+)\)', exc.detail)

    column = match.group('column')
    value = match.group('value')

    # value нужно привести к типу столбца
    model = next(
        model for model
        in apps.get_models()
        if model._meta.db_table == exc.table_name
    )
    field = next(
        field for field
        in model._meta.get_fields()
        if field.get_attname_column()[1] == column
    )
    value = field.to_python(value)

    return model, field, value
