import asyncio
import contextlib
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, List, Optional

from aioredis import ConnectionsPool, Redis, create_pool

from dropland.log import logger, tr
from dropland.storages.base import StorageBackend, StorageEngine


@dataclass
class EngineConfig:
    url: str
    max_connections: int = 4
    pool_timeout_seconds: int = 5


class RedisStorageBackend(StorageBackend):
    def __init__(self):
        self._engines: Dict[str, 'RedisStorageEngine'] = dict()

    @property
    def name(self) -> str:
        return 'redis'

    def create_engine(self, name: str, config: EngineConfig,
                      default_ttl: timedelta = timedelta(seconds=60)) -> Optional['RedisStorageEngine']:
        if engine := self._engines.get(name):
            return engine

        engine = RedisStorageEngine(self, name, config, default_ttl)
        self._engines[name] = engine
        logger.info(tr('dropland.storage.redis.engine.created'))
        return engine

    def get_engine(self, name: str) -> Optional['RedisStorageEngine']:
        return self._engines.get(name)

    def get_engine_names(self) -> List[str]:
        return list(self._engines.keys())


class RedisStorageEngine(StorageEngine):
    def __init__(self, backend: RedisStorageBackend, name: str, config: EngineConfig, default_ttl: timedelta):
        super().__init__(backend)
        self._name = name
        self._config = config
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
        self._pool: ConnectionsPool = None
        self._counter = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_async(self):
        return True

    @property
    def default_ttl(self) -> timedelta:
        return self._default_ttl

    def new_connection(self):
        @contextlib.asynccontextmanager
        async def inner(self):
            yield Redis(self._pool)
        return inner(self)

    def start(self):
        raise RuntimeError('Use async_start method')

    def stop(self):
        raise RuntimeError('Use async_stop method')

    async def async_start(self):
        async with self._lock:
            if 0 == self._counter:
                assert not self._pool
                self._pool = await create_pool(
                    self._config.url, create_connection_timeout=self._config.pool_timeout_seconds,
                    minsize=1, maxsize=self._config.max_connections
                )
                logger.info(tr('dropland.storage.redis.engine.started'))
            self._counter += 1

    async def async_stop(self):
        async with self._lock:
            if 1 == self._counter:
                assert self._pool
                self._pool.close()
                await self._pool.wait_closed()
                self._pool = None
                logger.info(tr('dropland.storage.redis.engine.stopped'))

            self._counter = max(self._counter - 1, 0)

    # noinspection PyPep8Naming,PyTypeChecker
    @property
    def Model(self) -> 'Model':
        from dropland.storages.redis.model import RedisModel, SimpleRedisModelBase

        attributes = {'_redis_engine': self}
        return RedisModel('RedisModel', (SimpleRedisModelBase,), attributes)

    # noinspection PyPep8Naming,PyTypeChecker
    @property
    def HashModel(self) -> 'Model':
        from dropland.storages.redis.model import RedisModel, HashRedisModelBase

        attributes = {'_redis_engine': self}
        return RedisModel('RedisModel', (HashRedisModelBase,), attributes)
