import contextlib
import pickle
from collections import OrderedDict
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from dependency_injector.wiring import Provide, inject

from dropland.data.context import ContextData
from dropland.storages.base import CacheModel
from dropland.storages.redis import RedisStorageEngine
from dropland.storages.redis.connections import ConnectionManager


class RedisModel(type):
    def __init__(cls, class_name, parents, attributes):
        super().__init__(class_name, parents, attributes)

    @inject
    def __new__(mcs, class_name, parents, attributes, manager: ConnectionManager = Provide['manager']):
        rv = super().__new__(mcs, class_name, parents, attributes)
        if isinstance(manager, ConnectionManager):
            rv._redis_manager = manager
        return rv

    # noinspection PyUnresolvedReferences
    @property
    def _model_cache_key(cls):
        return f'{cls._redis_engine.name}.models.{cls.__name__}'


class RedisModelBase(CacheModel, metaclass=RedisModel):
    __metaclass__ = RedisModel
    _redis_engine: RedisStorageEngine = None
    _redis_manager: ConnectionManager = None

    @classmethod
    def get_model_cache_key(cls) -> str:
        return cls._model_cache_key

    @classmethod
    def get_engine(cls) -> RedisStorageEngine:
        return cls._redis_engine

    @classmethod
    @contextlib.asynccontextmanager
    async def _async_connection_context(cls, ctx: ContextData = None):
        ctx = ctx if ctx else ContextData()
        if hasattr(ctx, 'redis'):
            yield ctx
        else:
            async with cls._redis_manager.async_connection_context(cls._redis_engine.name) as c:
                ctx.redis = c
                yield ctx
                del ctx.redis


class SimpleRedisModelBase(RedisModelBase):
    @classmethod
    async def _cache_one(
        cls, ctx: ContextData, instance: Optional['RedisModelBase'] = None,
            id_value: Optional[Any] = None, data: Optional[Dict[str, Any]] = None,
            exp: Optional[timedelta] = None, **kwargs) -> bool:
        cache_kwargs = dict()
        if instance and id_value is None:
            id_value = instance.get_id_value()

        if cls.Meta.cache_ttl_enable:
            expiration = exp or ctx.data.get(f'exp/{cls.get_model_cache_key()}', ctx.redis.engine.default_ttl)
            total_seconds = expiration.total_seconds()

            if total_seconds > 1:
                cache_kwargs['expire'] = int(total_seconds)
            elif 0 < total_seconds < 1:
                cache_kwargs['pexpire'] = int(total_seconds * 1000)
            else:
                total_seconds = ctx.redis.engine.default_ttl.total_seconds()
                cache_kwargs['expire'] = int(total_seconds) if total_seconds > 1 else 60

        if data:
            data = pickle.dumps(data)
        else:
            data = instance.serialize() if instance else pickle.dumps(None)

        return bool(await ctx.redis.connection.set(cls.get_cache_key(id_value), data, **cache_kwargs))

    @classmethod
    async def _cache_many(
            cls, ctx: ContextData, objects: List['RedisModelBase'], exp: timedelta = None, **kwargs) -> bool:
        if not objects:
            return False
        model_cache_key = cls.get_model_cache_key()
        res = False

        tx = ctx.redis.connection.multi_exec()

        for instance in objects:
            cache_kwargs = dict()

            if cls.Meta.cache_ttl_enable:
                expiration = exp or ctx.data.get(f'exp/{model_cache_key}', ctx.redis.engine.default_ttl)
                total_seconds = expiration.total_seconds()

                if total_seconds > 1:
                    cache_kwargs['expire'] = int(total_seconds)
                elif 0 < total_seconds < 1:
                    cache_kwargs['pexpire'] = int(total_seconds * 1000)
                else:
                    total_seconds = ctx.redis.engine.default_ttl.total_seconds()
                    cache_kwargs['expire'] = int(total_seconds) if total_seconds > 1 else 60

            tx.set(cls.get_cache_key(instance.get_id_value()), instance.serialize(), **cache_kwargs)

        for r in await tx.execute():
            res |= r

        return bool(res)

    @classmethod
    async def _load_one(
            cls, ctx: ContextData, cache_key: str, **kwargs) -> Tuple[bool, Optional[Dict[str, Any]]]:
        if res := await ctx.redis.connection.get(cache_key):
            return True, cls.deserialize(res)
        return False, None

    @classmethod
    async def _load_many(
            cls, ctx: ContextData, indices: List[Any], **kwargs) -> List[Optional[Dict[str, Any]]]:
        if not indices:
            return []
        cache_keys = [cls.get_cache_key(id_value) for id_value in indices]
        res = await ctx.redis.connection.mget(*cache_keys)
        objects: Dict[Any, Any] = OrderedDict()
        for id_value, data in zip(indices, res):
            objects[id_value] = cls.deserialize(data) if data is not None else None
        return list(objects.values())

    @classmethod
    async def _drop_one(cls, ctx: ContextData, cache_key: str) -> bool:
        return bool(await ctx.redis.connection.delete(cache_key))

    @classmethod
    async def _drop_many(cls, ctx: ContextData, indices: List[Any] = None) -> bool:
        if indices and len(indices) > 0:
            cache_keys = [cls.get_cache_key(id_value) for id_value in indices]
        else:
            model_cache_key = cls.get_model_cache_key()
            cache_keys = await ctx.redis.connection.keys(f'{model_cache_key}:*')

        return bool(await ctx.redis.connection.delete(*cache_keys)) if cache_keys else False

    @classmethod
    async def _exists(cls, ctx: ContextData, cache_key: str) -> bool:
        if await ctx.redis.connection.exists(cache_key):
            return await ctx.redis.connection.get(cache_key) != pickle.dumps(None)
        return False

    @classmethod
    async def _scan(cls, ctx: ContextData, cache_key: str = None,
                    match: str = None, count: int = None) -> Tuple[str, Optional[Dict[str, Any]]]:
        match = f'{cache_key}:{match}' if cache_key and match else match
        async for k in ctx.redis.connection.iscan(match=match, count=count):
            cache_key = k.decode('utf-8')
            yield cache_key.split(':')[1] if ':' in cache_key else cache_key, (await cls._load_one(ctx, cache_key))[1]


class HashRedisModelBase(RedisModelBase):
    @classmethod
    async def _cache_one(
        cls, ctx: ContextData, instance: Optional['RedisModelBase'] = None,
            id_value: Optional[Any] = None, data: Optional[Dict[str, Any]] = None,
            exp: Optional[timedelta] = None, **kwargs) -> bool:
        if instance and id_value is None:
            id_value = instance.get_id_value()

        model_cache_key, cache_id = cls.get_model_cache_key(), cls.get_cache_id(id_value)

        if data:
            data = pickle.dumps(data)
        else:
            data = instance.serialize() if instance else pickle.dumps(None)

        if cls.Meta.cache_ttl_enable:
            res = False
            tx = ctx.redis.connection.multi_exec()
            expiration = ctx.data.get(f'exp/{model_cache_key}', ctx.redis.engine.default_ttl)
            tx.hset(model_cache_key, cache_id, data)
            tx.expire(model_cache_key, int(expiration.total_seconds()))

            for r in await tx.execute():
                res |= r

            return bool(res)

        return bool(await ctx.redis.connection.hset(model_cache_key, cache_id, data))

    @classmethod
    async def _cache_many(
            cls, ctx: ContextData, objects: List['RedisModelBase'], exp: timedelta = None, **kwargs) -> bool:
        if not objects:
            return False
        model_cache_key = cls.get_model_cache_key()
        obj_dict = {cls.get_cache_id(instance.get_id_value()): instance.serialize() for instance in objects}

        if cls.Meta.cache_ttl_enable:
            res = False
            tx = ctx.redis.connection.multi_exec()
            expiration = ctx.data.get(f'exp/{model_cache_key}', ctx.redis.engine.default_ttl)
            tx.hmset_dict(model_cache_key, obj_dict)
            tx.expire(model_cache_key, int(expiration.total_seconds()))

            for r in await tx.execute():
                res |= r

            return bool(res)

        return bool(await ctx.redis.connection.hmset_dict(model_cache_key, obj_dict))

    @classmethod
    async def _load_one(
            cls, ctx: ContextData, cache_key: str, **kwargs) -> Tuple[bool, Optional[Dict[str, Any]]]:
        if ':' in cache_key:
            model_cache_key, cache_id = cache_key.split(':')
            if res := await ctx.redis.connection.hget(model_cache_key, cache_id):
                return True, cls.deserialize(res)
            return False, None
        else:
            if res := await ctx.redis.connection.get(cache_key):
                return True, cls.deserialize(res)
            return False, None

    @classmethod
    async def _load_many(
            cls, ctx: ContextData, indices: List[Any], **kwargs) -> List[Optional[Dict[str, Any]]]:
        if not indices:
            return []
        cache_keys = [cls.get_cache_id(id_value) for id_value in indices]
        res = await ctx.redis.connection.hmget(cls.get_model_cache_key(), *cache_keys)
        objects: Dict[Any, Any] = OrderedDict()
        for id_value, data in zip(indices, res):
            objects[id_value] = cls.deserialize(data) if data is not None else None
        return list(objects.values())

    @classmethod
    async def _drop_one(cls, ctx: ContextData, cache_key: str) -> bool:
        if ':' in cache_key:
            model_cache_key, cache_id = cache_key.split(':')
            return bool(await ctx.redis.connection.hdel(model_cache_key, cache_id))
        else:
            return bool(await ctx.redis.connection.delete(cache_key))

    @classmethod
    async def _drop_many(cls, ctx: ContextData, indices: List[Any] = None) -> bool:
        model_cache_key = cls.get_model_cache_key()

        if indices and len(indices) > 0:
            cache_keys = [cls.get_cache_id(id_value) for id_value in indices]
        else:
            cache_keys = await ctx.redis.connection.hkeys(model_cache_key)

        return bool(await ctx.redis.connection.hdel(model_cache_key, *cache_keys)) if cache_keys else False

    @classmethod
    async def _exists(cls, ctx: ContextData, cache_key: str) -> bool:
        if ':' in cache_key:
            model_cache_key, cache_id = cache_key.split(':')
            e = bool(await ctx.redis.connection.hexists(model_cache_key, cache_id))
        else:
            e = bool(await ctx.redis.connection.exists(cache_key))
        if e:
            return await ctx.redis.connection.get(cache_key) != pickle.dumps(None)
        return False

    @classmethod
    async def _scan(cls, ctx: ContextData, cache_key: str = None,
                    match: str = None, count: int = None) -> Tuple[str, Optional[Dict[str, Any]]]:
        async for k, data in ctx.redis.connection.ihscan(cache_key, match=match, count=count):
            yield k.decode('utf-8'), cls.deserialize(data)
