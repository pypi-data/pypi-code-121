import contextlib
from typing import Any, Dict, List, Optional, Set, Type

from dropland.core.metaclass import classmaker
from dropland.data.context import ContextData
from dropland.storages import CacheModel
from dropland.storages.sql import SqlModel


class CachedModelImpl:
    @classmethod
    def has_cache(cls):
        return True

    # noinspection PyUnresolvedReferences
    @classmethod
    def get_engine(cls):
        return cls._sql_class.get_engine()

    # noinspection PyUnresolvedReferences,PyProtectedMember
    @classmethod
    @contextlib.contextmanager
    def _connection_context(cls, begin_tx: bool = False, autocommit: bool = False, ctx: ContextData = None):
        with cls._sql_class._connection_context(begin_tx, autocommit, ctx) as ctx:
            yield ctx

    # noinspection PyUnresolvedReferences,PyProtectedMember
    @classmethod
    @contextlib.asynccontextmanager
    async def _async_connection_context(cls, begin_tx: bool = False, autocommit: bool = False, ctx: ContextData = None):
        async with cls._sql_class._async_connection_context(begin_tx, autocommit, ctx) as ctx:
            async with cls._cache_class._async_connection_context(ctx) as ctx:
                yield ctx

    #
    # Query operations
    #

    # noinspection PyUnresolvedReferences
    @classmethod
    def query_get(cls, id_value: Any, **kwargs):
        return id_value, super().query_get(id_value, **kwargs)

    # noinspection PyUnresolvedReferences
    @classmethod
    def query_any(cls, indices: List[Any], **kwargs):
        return indices, super().query_any(indices, **kwargs)

    # noinspection PyUnresolvedReferences
    @classmethod
    def query_count(cls, filters: Optional[List[Any]] = None, params: Dict[str, Any] = None, **kwargs):
        if not filters or not isinstance(filters, list):
            cache_key = f'{cls.get_model_cache_key()}.count'
        else:
            cache_key = None

        return cache_key, super().query_count(filters, params, **kwargs)

    # noinspection PyUnresolvedReferences
    @classmethod
    def query_exists(cls, id_value: Any, **kwargs):
        return cls.get_cache_key(id_value), super().query_exists(id_value, **kwargs)

    #
    # Perform operations
    #

    # noinspection PyUnresolvedReferences
    @classmethod
    async def perform_get(cls, ctx: ContextData, query, **kwargs) -> Optional['CachedModelImpl']:
        id_value, query = query[0], query[1]
        exists, data = await cls._load_one(ctx, cls.get_cache_key(id_value), **kwargs)
        if exists:
            if data is not None:
                if orm_cached := (await cls._get_from_orm_cache(ctx, [id_value]))[0]:
                    return orm_cached
            return await cls.construct(ctx, data, **kwargs)

        instance = await super().perform_get(ctx, query, **kwargs)
        await cls._cache_one(ctx, instance, id_value)
        return instance

    # noinspection PyUnresolvedReferences
    @classmethod
    async def perform_list(cls, ctx: ContextData, query, **kwargs) -> List['CachedModelImpl']:
        objects = await super().perform_list(ctx, query, **kwargs)
        await cls._cache_many(ctx, objects, **kwargs)
        await cls._drop_one(ctx, f'{cls.get_model_cache_key()}.count')
        return objects

    # noinspection PyUnresolvedReferences
    @classmethod
    async def perform_any(cls, ctx: ContextData, query, **kwargs) -> List[Optional['CachedModelImpl']]:
        indices, query = query[0], query[1]
        cached_indices, non_cached_indices = list(), list()

        cached_objects = await cls._load_many(ctx, indices, **kwargs)

        for id_value, instance in zip(indices, cached_objects):
            if instance is None:
                non_cached_indices.append(id_value)
            else:
                cached_indices.append(id_value)

        orm_cached_objects = {
            id_value: obj for id_value, obj in
            zip(cached_indices, await cls._get_from_orm_cache(ctx, cached_indices))
        }

        for id_value, (i, instance) in zip(indices, enumerate(cached_objects)):
            if id_value in orm_cached_objects:
                if obj := orm_cached_objects[id_value]:
                    cached_objects[i] = obj

        if not non_cached_indices:
            return await cls.construct_list(ctx, cached_objects, **kwargs)
        elif cached_objects:
            query = super().query_any(non_cached_indices, **kwargs)

        non_cached_objects = await super().perform_any(ctx, query, **kwargs)
        await cls._cache_many(ctx, non_cached_objects, **kwargs)

        cached_objects = await cls.construct_list(ctx, cached_objects, **kwargs)
        cached_objects = {id_value: obj for id_value, obj in zip(indices, cached_objects) if obj is not None}
        non_cached_objects = {obj.get_id_value(): obj for obj in non_cached_objects}
        result = []

        for id_value in indices:
            if id_value in non_cached_objects:
                result.append(non_cached_objects[id_value])
            elif id_value in cached_objects:
                result.append(cached_objects[id_value])

        return result

    # noinspection PyUnresolvedReferences
    @classmethod
    async def perform_count(cls, ctx: ContextData, query, **kwargs) -> int:
        cache_key, query = query[0], query[1]

        if cache_key:
            res = await ctx.redis.connection.get(cache_key)
            if res is not None:
                return int(res)

        res = await super().perform_count(ctx, query, **kwargs)

        if res and cache_key:
            cache_kwargs = dict()

            if cls.Meta.cache_ttl_enable:
                total_seconds = ctx.redis.engine.default_ttl.total_seconds()
                cache_kwargs['expire'] = int(total_seconds) if total_seconds > 1 else 60

            await ctx.redis.connection.set(cache_key, res, **cache_kwargs)

        return res

    # noinspection PyUnresolvedReferences
    @classmethod
    async def perform_exists(cls, ctx: ContextData, query, **kwargs) -> bool:
        cache_key, query = query[0], query[1]
        if await cls._exists(ctx, cache_key):
            return True
        return await super().perform_exists(ctx, query, **kwargs)

    # noinspection PyUnresolvedReferences
    @classmethod
    async def perform_exists_by(cls, ctx: ContextData, query, **kwargs) -> bool:
        return await super().perform_exists_by(ctx, query, **kwargs)

    # noinspection PyUnresolvedReferences
    @classmethod
    async def perform_create(cls, ctx: ContextData, data: Dict[str, Any]) -> Optional['CachedModelImpl']:
        instance = await super().perform_create(ctx, data)
        await cls._cache_one(ctx, instance)
        await cls._drop_one(ctx, f'{cls.get_model_cache_key()}.count')
        return instance

    # noinspection PyUnresolvedReferences
    @classmethod
    async def perform_update(
            cls, ctx: ContextData, data: Dict[str, Any], id_value: Any) -> Optional[Dict[str, Any]]:
        data = await super().perform_update(ctx, data, id_value)
        await cls._drop_one(ctx, cls.get_cache_key(id_value))
        return data

    # noinspection PyUnresolvedReferences
    @classmethod
    async def perform_delete(cls, ctx: ContextData, id_value: Any) -> bool:
        if res := await super().perform_delete(ctx, id_value):
            await cls._drop_one(ctx, cls.get_cache_key(id_value))
            await cls._drop_one(ctx, f'{cls.get_model_cache_key()}.count')
        return res

    # noinspection PyUnresolvedReferences
    async def perform_save(
        self, ctx: ContextData, data: Dict[str, Any], updated_fields: Set[str], **kwargs) \
            -> Optional[Dict[str, Any]]:
        if data := await super().perform_save(ctx, data, updated_fields, **kwargs):
            await self._cache_one(ctx, self, data=data)
        return data

    # noinspection PyUnresolvedReferences
    async def perform_load(self, ctx: ContextData, field_names: List[str] = None) -> bool:
        id_value = self.get_id_value()
        exists, data = await self._load_one(ctx, self.get_cache_key(id_value))
        if exists and isinstance(data, dict):
            await self.assign(data).reload_rela(ctx, field_names)
            return True

        if res := await super().perform_load(ctx, attribute_names):
            await cls._cache_one(ctx, self)
        return res

    # noinspection PyUnresolvedReferences
    @classmethod
    async def perform_save_all(cls, ctx: ContextData, objects: List['CachedModelImpl'], **kwargs) -> bool:
        if res := await super().perform_save_all(ctx, objects, **kwargs):
            await cls._cache_many(ctx, objects, **kwargs)
            await cls._drop_one(ctx, f'{cls.get_model_cache_key()}.count')
        return res


# noinspection PyPep8Naming
def CachedModel(cache_name: str, sql_class: Type[SqlModel], cache_class: Type[CacheModel]):
    # noinspection PyShadowingNames,PyUnresolvedReferences
    class CachedModel(sql_class.__metaclass__, cache_class.__metaclass__):
        # noinspection PyUnresolvedReferences
        @property
        def _model_cache_key(self):
            return f'{cache_name}.models.{self.__tablename__}'

    # noinspection PyAbstractClass
    class CachedModelClass(CachedModelImpl, sql_class, cache_class, metaclass=CachedModel):
        __abstract__ = True
        __metaclass__ = classmaker()
        _sql_class = sql_class
        _cache_class = cache_class

    return CachedModelClass
