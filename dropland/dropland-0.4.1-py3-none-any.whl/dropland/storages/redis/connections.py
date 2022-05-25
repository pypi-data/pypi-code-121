import asyncio
import contextlib
from dataclasses import dataclass, replace
from typing import Dict, List, Mapping, Optional, Tuple

from aioredis import Redis as RedisConnection
from contextvars import ContextVar

from dropland.storages.redis.engine import RedisStorageEngine, RedisStorageBackend


@dataclass
class ConnectionData:
    engine: RedisStorageEngine
    connection: RedisConnection


class ConnectionContext:
    def __init__(self):
        self.conns: Dict[str, ConnectionData] = dict()


class ConnectionManager:
    def __init__(self, engine_factory: RedisStorageBackend):
        self._ctx: ContextVar[ConnectionContext] = ContextVar('_ctx')
        self._engine_factory = engine_factory

    def get_connection(self, name: str) -> Optional[ConnectionData]:
        if ctx := self._ctx.get(None):
            return ctx.conns.get(name)
        return None

    def get_or_create_connection(self, name: str) -> Tuple[bool, Optional[ConnectionData]]:
        if conn := self.get_connection(name):
            return False, conn

        if engine := self._engine_factory.get_engine(name):
            return True, ConnectionData(
                engine=engine,
                connection=engine.new_connection())

        return False, None

    def _add_connection(self, name: str, data: ConnectionData) -> ConnectionData:
        if ctx := self._ctx.get(None):
            ctx.conns[name] = data
        return data

    def _remove_connection(self, name: str):
        if ctx := self._ctx.get(None):
            ctx.conns.pop(name)

    @contextlib.asynccontextmanager
    async def async_connection_context(self, name: str):
        created, data = self.get_or_create_connection(name)

        if not created:
            yield data
            return

        async with data.connection as conn:
            data = replace(data, connection=conn)
            yield self._add_connection(name, data)
            self._remove_connection(name)

    @contextlib.asynccontextmanager
    async def _with_async_engines_context(self, engines: Mapping[str, RedisStorageEngine]):
        ctx = ConnectionContext()
        token = self._ctx.set(ctx)
        try:
            async with contextlib.AsyncExitStack() as stack:
                for name, engine in engines.items():
                    assert engine is self._engine_factory.get_engine(name)
                    if engine.is_async:
                        await engine.async_start()
                        stack.push_async_callback(engine.async_stop)
                    else:
                        engine.start()
                        stack.callback(engine.stop)

                    await stack.enter_async_context(self.async_connection_context(name))
                yield ctx
        finally:
            if self._ctx.get(None) is ctx:
                self._ctx.reset(token)

    @contextlib.contextmanager
    def set_context(self, ctx: ConnectionContext):
        token = self._ctx.set(ctx)
        yield
        self._ctx.reset(token)

    def get_engines(self, names: List[str]) -> Mapping[str, RedisStorageEngine]:
        engines = dict()

        if not names:
            names = self._engine_factory.get_engine_names()

        for name in names:
            if engine := self._engine_factory.get_engine(name):
                engines[name] = engine

        return engines

    @contextlib.asynccontextmanager
    async def with_async_engines(self, names: List[str] = None):
        engines = self.get_engines(names or [])
        async with self._with_async_engines_context(engines) as ctx:
            yield ctx

    def use_engines(self, names: List[str] = None):
        def inner(function):
            assert asyncio.iscoroutinefunction(function)
            engines = self.get_engines(names or [])

            async def decorator(*args, **kwargs):
                async with self._with_async_engines_context(engines):
                    return await function(*args, **kwargs)

            return decorator
        return inner
