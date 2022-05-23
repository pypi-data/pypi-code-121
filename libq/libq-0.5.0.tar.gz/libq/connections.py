import asyncio
import functools
import json
import logging
import ssl
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union
from urllib.parse import urlparse

from pydantic.validators import make_arbitrary_type_validator
from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.sentinel import Sentinel
from redis.exceptions import RedisError, WatchError

from libq import defaults
from libq.logs import logger
from libq.utils import generate_random


class SSLContext(ssl.SSLContext):
    """
    Required to avoid problems with
    """

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., Any], None, None]:
        yield make_arbitrary_type_validator(ssl.SSLContext)


@dataclass
class RedisSettings:
    """
    No-Op class used to hold redis connection redis_settings.
    Used by :func:`streamq.connections.create_pool` and :class:`streamq.worker.Worker`.
    """

    host: str = 'localhost'
    port: int = 6379
    database: int = 0
    username: Optional[str] = None
    password: Optional[str] = None
    ssl: Union[bool, None, SSLContext] = None
    conn_timeout: int = 1
    conn_retries: int = 5
    conn_retry_delay: int = 1
    decode_responses: bool = True

    sentinel: bool = False
    sentinel_master: str = 'mymaster'

    @classmethod
    def from_dsn(cls, dsn: str, decode_responses=True) -> 'RedisSettings':
        conf = urlparse(dsn)
        assert conf.scheme in {'redis', 'rediss'}, 'invalid DSN scheme'
        return RedisSettings(
            host=conf.hostname or 'localhost',
            port=conf.port or 6379,
            ssl=conf.scheme == 'rediss',
            username=conf.username,
            password=conf.password,
            database=int((conf.path or '0').strip('/')),
            decode_responses=decode_responses
        )

    def __repr__(self) -> str:
        return 'RedisSettings({})'.format(', '.join(f'{k}={v!r}' for k, v in self.__dict__.items()))


# class Driver(Redis):  # type: ignore[misc]
#     def __init__(self,
#                  pool_or_conn: Optional[ConnectionPool] = None,
#                  # job_serializer: Optional[Serializer] = None,
#                  # job_deserializer: Optional[Deserializer] = None,
#                  # default_queue_name: str = defaults.QUEUE_NAME,
#                  **kwargs: Any,
#                  ) -> None:
#         # self.job_serializer = job_serializer
#         # self.job_deserializer = job_deserializer
#         # self.default_queue_name = default_queue_name
#         if pool_or_conn:
#             kwargs['connection_pool'] = pool_or_conn
#         super().__init__(**kwargs)


async def create_pool_ping(
    settings_: RedisSettings = None,
    *,
    retry: int = 0,
) -> Redis:
    """
    Create a new redis pool, retrying up to ``conn_retries`` times if the connection fails.
    Returns a :class:`arq.connections.ArqRedis` instance, thus allowing job enqueuing.
    """
    settings: RedisSettings = RedisSettings() if settings_ is None else settings_

    assert not (
        type(settings.host) is str and settings.sentinel
    ), "str provided for 'host' but 'sentinel' is true; list of sentinels expected"

    if settings.sentinel:

        def pool_factory(*args: Any, **kwargs: Any) -> Redis:
            client = Sentinel(*args, sentinels=settings.host,
                              ssl=settings.ssl, **kwargs)
            return client.master_for(settings.sentinel_master)

    else:
        pool_factory = functools.partial(
            Redis,
            host=settings.host,
            port=settings.port,
            socket_connect_timeout=settings.conn_timeout,
            ssl=settings.ssl,
            decode_responses=settings.decode_responses,
        )

    try:
        pool = pool_factory(
            db=settings.database, username=settings.username, password=settings.password, encoding='utf8'
        )
        await pool.ping()

    except (ConnectionError, OSError, RedisError, asyncio.TimeoutError) as e:
        if retry < settings.conn_retries:
            logger.warning(
                'redis connection error %s:%s %s %s, %d retries remaining...',
                settings.host,
                settings.port,
                e.__class__.__name__,
                e,
                settings.conn_retries - retry,
            )
            await asyncio.sleep(settings.conn_retry_delay)
        else:
            raise
    else:
        if retry > 0:
            logger.info('redis connection successful')
        return pool

    # recursively attempt to create the pool outside the except block to avoid
    # "During handling of the above exception..." madness
    return await create_pool_ping(
        settings,
        retry=retry + 1,
    )


def create_pool(
    settings_: RedisSettings = None,
    *,
    retry: int = 0,
) -> Redis:
    """
    Create a new redis pool, retrying up to ``conn_retries`` times if the connection fails.
    Returns a :class:`arq.connections.ArqRedis` instance, thus allowing job enqueuing.
    """
    settings: RedisSettings = RedisSettings() if settings_ is None else settings_

    assert not (
        type(settings.host) is str and settings.sentinel
    ), "str provided for 'host' but 'sentinel' is true; list of sentinels expected"

    if settings.sentinel:

        def pool_factory(*args: Any, **kwargs: Any) -> Redis:
            client = Sentinel(*args, sentinels=settings.host,
                              ssl=settings.ssl, **kwargs)
            return client.master_for(settings.sentinel_master)

    else:
        pool_factory = functools.partial(
            Redis,
            host=settings.host,
            port=settings.port,
            socket_connect_timeout=settings.conn_timeout,
            ssl=settings.ssl,
            decode_responses=settings.decode_responses,
        )

    pool = pool_factory(
        db=settings.database, username=settings.username, password=settings.password, encoding='utf8'
    )
    return pool


def create_pool_dsn(url, decode_responses=True) -> Redis:
    settings = RedisSettings.from_dsn(url, decode_responses)
    conn = create_pool(settings)
    return conn
