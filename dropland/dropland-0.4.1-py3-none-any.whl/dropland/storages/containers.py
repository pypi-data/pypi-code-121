import contextlib
from datetime import timedelta
from typing import List

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from pytimeparse.timeparse import timeparse

from dropland.storages.redis import USE_REDIS
from dropland.storages.sql import USE_SQL
from dropland.util import default_value

if USE_REDIS:
    from dropland.storages.redis.connections import ConnectionManager as RedisConnectionManager
    from dropland.storages.redis.engine import RedisStorageBackend, EngineConfig as RedisEngineConfig

if USE_SQL:
    from dropland.storages.sql.connections import ConnectionManager as SqlConnectionManager
    from dropland.storages.sql.engine import EngineFactory as SqlEngineFactory, EngineConfig as SqlEngineConfig
    from dropland.storages.sql.loader import SqlBackendLoader


if USE_SQL:
    import dropland.storages.sql.model

    class SqlStorage(containers.DeclarativeContainer):
        __self__ = providers.Self()
        backend_loader = providers.Singleton(SqlBackendLoader)
        engine_factory = providers.Singleton(SqlEngineFactory, backend_loader)
        manager = providers.Singleton(SqlConnectionManager, engine_factory)

        def _create_engine(self, *args, **kwargs):
            return self.engine_factory().create_engine(*args, **kwargs)

        create_engine = providers.Factory(_create_engine, __self__)
        wiring_config = containers.WiringConfiguration(modules=[dropland.storages.sql.model, __name__])


    class SingleSqlStorage(SqlStorage):
        __self__ = providers.Self()
        config = providers.Configuration()

        def _create_engine(self):
            if isinstance(self.config.engine_config(), SqlEngineConfig):
                engine_config = self.config.engine_config()
            else:
                engine_config = SqlEngineConfig(
                    url=self.config.engine_config.url(),
                    echo=self.config.engine_config.echo.as_(bool)(),
                    pool_min_size=self.config.engine_config.
                        pool_min_size.as_(default_value(int))(default=1),
                    pool_max_size=self.config.engine_config.
                        pool_max_size.as_(default_value(int))(default=8),
                    pool_expire_seconds=self.config.engine_config.
                        pool_expire_seconds.as_(default_value(int))(default=60),
                    pool_timeout_seconds=self.config.engine_config.
                        pool_timeout_seconds.as_(default_value(int))(default=15)
                )
            return SqlStorage._create_engine(
                self, self.config.db_type(), engine_config, backend_name=self.config.backend_name(),
                use_async=self.config.use_async.as_(bool)())

        create_engine = providers.Factory(_create_engine, __self__)
        wiring_config = containers.WiringConfiguration(modules=[dropland.storages.sql.model, __name__])


    class MultipleSqlStorage(SqlStorage):
        __self__ = providers.Self()
        config = providers.Configuration()

        def _create_engine(self, name: str):
            if conf := self.config.get(name):
                if isinstance(conf['engine_config'], SqlEngineConfig):
                    engine_config = conf['engine_config']
                else:
                    engine_config = SqlEngineConfig(
                        url=conf['engine_config']['url'],
                        echo=bool(conf['engine_config'].get('echo')),
                        pool_min_size=int(conf['engine_config'].get('pool_min_size', 1)),
                        pool_max_size=int(conf['engine_config'].get('pool_max_size', 8)),
                        pool_expire_seconds=int(conf['engine_config'].get('pool_expire_seconds', 60)),
                        pool_timeout_seconds=int(conf['engine_config'].get('pool_timeout_seconds', 15))
                    )
                return SqlStorage._create_engine(
                    self, conf['db_type'], engine_config, backend_name=conf.get('backend_name'),
                    use_async=conf.get('use_async', False))
            return None

        create_engine = providers.Factory(_create_engine, __self__)
        wiring_config = containers.WiringConfiguration(modules=[dropland.storages.sql.model, __name__])

    default_sql_storage = SqlStorage()
else:
    class SqlStorage:
        manager = None


if USE_REDIS:
    import dropland.storages.redis.model

    class RedisStorage(containers.DeclarativeContainer):
        __self__ = providers.Self()
        engine_factory = providers.Singleton(RedisStorageBackend)
        manager = providers.Singleton(RedisConnectionManager, engine_factory)
        default_ttl = providers.Object(timedelta(seconds=timeparse('1 min')))

        def _create_engine(self, *args, **kwargs):
            return self.engine_factory().create_engine(*args, **kwargs)

        create_engine = providers.Factory(_create_engine, __self__)
        wiring_config = containers.WiringConfiguration(modules=[dropland.storages.redis.model, __name__])


    class SingleRedisStorage(RedisStorage):
        __self__ = providers.Self()
        config = providers.Configuration()
        default_ttl = providers.Object(timedelta(
            seconds=timeparse(config.get('default_cache_ttl', required=False) or '1 min')))

        def _create_engine(self):
            if isinstance(self.config.engine_config(), RedisEngineConfig):
                engine_config = self.config.engine_config()
            else:
                engine_config = RedisEngineConfig(
                    url=self.config.engine_config.url(),
                    max_connections=self.config.engine_config.
                        max_connections.as_(default_value(int))(default=4),
                    pool_timeout_seconds=self.config.engine_config.
                        pool_timeout_seconds.as_(default_value(int))(default=5)
                )
            return RedisStorage._create_engine(self, self.config.name(), engine_config, self.default_ttl())

        create_engine = providers.Factory(_create_engine, __self__)
        wiring_config = containers.WiringConfiguration(modules=[dropland.storages.redis.model, __name__])


    class MultipleRedisStorage(RedisStorage):
        __self__ = providers.Self()
        config = providers.Configuration()

        def _create_engine(self, name: str):
            if conf := self.config.get(name):
                if isinstance(conf['engine_config'], RedisEngineConfig):
                    engine_config = conf['engine_config']
                else:
                    engine_config = RedisEngineConfig(
                        url=conf['engine_config']['url'],
                        max_connections=int(conf['engine_config'].get('max_connections', 4)),
                        pool_timeout_seconds=int(conf['engine_config'].get('pool_timeout_seconds', 5))
                    )
                return RedisStorage._create_engine(
                    self, conf['name'], engine_config,
                    timedelta(seconds=timeparse(conf.get('default_cache_ttl', '1 min'))))
            return None

        create_engine = providers.Factory(_create_engine, __self__)
        wiring_config = containers.WiringConfiguration(modules=[dropland.storages.redis.model, __name__])

    default_redis_storage = RedisStorage()
else:
    class RedisStorage:
        manager = None


if USE_SQL or USE_REDIS:
    @inject
    def use_engines(
            sql_backends: List[str] = None,
            redis_names: List[str] = None,
            begin_sql_tx: bool = True,
            autocommit: bool = True,
            sql_manager: 'SqlConnectionManager' = Provide[SqlStorage.manager] if USE_SQL else None,
            redis_manager: 'RedisConnectionManager' = Provide[RedisStorage.manager] if USE_REDIS else None
            ):
        if USE_REDIS and isinstance(redis_manager, RedisConnectionManager):
            redis_inner = redis_manager.use_engines(redis_names)
        if USE_SQL and isinstance(sql_manager, SqlConnectionManager):
            sql_inner = sql_manager.use_engines(sql_backends, begin_sql_tx, autocommit)

        def inner(function):
            if USE_REDIS and isinstance(redis_manager, RedisConnectionManager):
                function = redis_inner(function)
            if USE_SQL and isinstance(sql_manager, SqlConnectionManager):
                function = sql_inner(function)
            return function

        return inner

    @contextlib.asynccontextmanager
    @inject
    async def with_async_engines(
            sql_backends: List[str] = None,
            redis_names: List[str] = None,
            begin_sql_tx: bool = True,
            autocommit: bool = True,
            sql_manager: 'SqlConnectionManager' = Provide[SqlStorage.manager] if USE_SQL else None,
            redis_manager: 'RedisConnectionManager' = Provide[RedisStorage.manager] if USE_REDIS else None
            ):
        async with contextlib.AsyncExitStack() as stack:
            if USE_REDIS and isinstance(redis_manager, RedisConnectionManager):
                await stack.enter_async_context(redis_manager.with_async_engines(redis_names))
            if USE_SQL and isinstance(sql_manager, SqlConnectionManager):
                await stack.enter_async_context(sql_manager.with_async_engines(sql_backends, begin_sql_tx, autocommit))
            yield
