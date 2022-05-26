import contextlib
from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Set, Tuple, TypeVar, Union

from dependency_injector.wiring import Provide, inject
from pydantic.main import BaseModel as PydanticModel
from sqlalchemy import Column, exists, func, literal_column, select, tuple_
from sqlalchemy.sql import ColumnCollection

from dropland.data.context import ContextData
from dropland.storages.base import StorageModel as BaseModel
from dropland.storages.sql import SqlStorageEngine, SqlStorageType
from dropland.storages.sql.connections import ConnectionManager

CreateSchemaType = TypeVar('CreateSchemaType', bound=PydanticModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=PydanticModel)


class SqlTableInfo(NamedTuple):
    db_type: SqlStorageType
    backend: str
    is_async: bool


class SqlModel(type):
    def __init__(cls, class_name, parents, attributes):
        super().__init__(class_name, parents, attributes)

    @inject
    def __new__(mcs, class_name, parents, attributes, manager: ConnectionManager = Provide['manager']):
        rv = super().__new__(mcs, class_name, parents, attributes)
        if isinstance(manager, ConnectionManager):
            rv._sql_manager = manager
        return rv


class SqlModelBase(BaseModel):
    _sql_engine: SqlStorageEngine = None
    _sql_manager: ConnectionManager = None

    # noinspection PyUnresolvedReferences
    @classmethod
    def _check_abstract(cls):
        if cls.__table__ is None:
            raise TypeError(f'Model {cls.__name__} is abstract, no table is defined!')

    def __eq__(self, other: 'SqlModel'):
        self._check_abstract()
        return type(self) == type(other) and self.get_id_value() == other.get_id_value()

    def __hash__(self):
        self._check_abstract()
        return self.get_id_value().__hash__()

    def get_id_value(self) -> Any:
        return self._get_column_values(self._get_id_columns())

    @classmethod
    def get_engine(cls) -> SqlStorageEngine:
        return cls._sql_engine

    @classmethod
    def get_table_info(cls) -> SqlTableInfo:
        engine = cls.get_engine()
        return SqlTableInfo(db_type=engine.db_type, backend=engine.backend.name, is_async=engine.is_async)

    @classmethod
    @contextlib.contextmanager
    def _connection_context(cls, begin_tx: bool = False, autocommit: bool = False, ctx: ContextData = None):
        info, ctx = cls.get_table_info(), ctx if ctx else ContextData()
        assert not info.is_async, 'Use async_connection_context() function instead'
        if hasattr(ctx, 'sql'):
            yield ctx
        else:
            with cls._sql_manager.connection_context(info.db_type, info.backend, begin_tx, autocommit) as c:
                ctx.sql = c
                yield ctx
                del ctx.sql

    @classmethod
    @contextlib.asynccontextmanager
    async def _async_connection_context(cls, begin_tx: bool = False, autocommit: bool = False, ctx: ContextData = None):
        info, ctx = cls.get_table_info(), ctx if ctx else ContextData()
        assert info.is_async, 'Use connection_context() function instead'
        if hasattr(ctx, 'sql'):
            yield ctx
        else:
            async with cls._sql_manager.async_connection_context(info.db_type, info.backend, begin_tx, autocommit) as c:
                ctx.sql = c
                yield ctx
                del ctx.sql

    @classmethod
    def get_db_query(cls, **kwargs):
        raise NotImplementedError

    # noinspection PyUnresolvedReferences
    @classmethod
    def get_columns(cls) -> ColumnCollection:
        return cls.__table__.columns

    # noinspection PyUnresolvedReferences,PyTypeChecker
    @classmethod
    def get_serializable_fields(cls) -> Set[str]:
        res = super().get_serializable_fields()
        res.difference_update({'metadata', 'registry'})
        return res

    # noinspection PyUnresolvedReferences,PyTypeChecker
    @classmethod
    def get_private_fields(cls) -> Set[str]:
        res = super().get_private_fields()
        res.update({'metadata', 'registry'})
        return res

    #
    # Retrieve operations
    #

    @classmethod
    async def get(cls, id_value: Any, **kwargs) -> Optional['SqlModel']:
        query = cls.query_get(id_value, **kwargs)
        async with cls._async_connection_context() as ctx:
            if instance := await cls.perform_get(ctx, query, **kwargs):
                return await cls.construct_rela(ctx, instance, **kwargs)
        return None

    @classmethod
    async def list(cls,
                   filters: Optional[List[Any]] = None,
                   sorting: Optional[List[Any]] = None,
                   skip: int = 0, limit: int = 0, params: Dict[str, Any] = None, **kwargs) -> List['SqlModel']:
        query = cls.query_list(filters or [], sorting or [], skip, limit, params, **kwargs)
        async with cls._async_connection_context() as ctx:
            objects = await cls.perform_list(ctx, query, **kwargs)
            return await cls.construct_rela_list(ctx, objects, **kwargs)

    @classmethod
    async def get_any(cls, indices: List[Any], **kwargs) -> List[Optional['SqlModel']]:
        query = cls.query_any(indices, **kwargs)
        async with cls._async_connection_context() as ctx:
            objects = await cls.perform_any(ctx, query, **kwargs)
            objects = await cls.construct_rela_list(ctx, objects, **kwargs)
        if len(objects) == len(indices):
            return objects
        objects = {obj.get_id_value(): obj for obj in objects}
        return [objects[id_value] if id_value in objects else None for id_value in indices]

    @classmethod
    async def count(cls, filters: Optional[List[Any]] = None, params: Dict[str, Any] = None, **kwargs) -> int:
        query = cls.query_count(filters, params, **kwargs)
        async with cls._async_connection_context() as ctx:
            return await cls.perform_count(ctx, query, **kwargs)

    @classmethod
    async def exists(cls, id_value: Any, **kwargs) -> bool:
        query = cls.query_exists(id_value, **kwargs)
        async with cls._async_connection_context() as ctx:
            return await cls.perform_exists(ctx, query, **kwargs)

    @classmethod
    async def exists_by(cls, filters: List[Any], params: Dict[str, Any] = None, **kwargs) -> bool:
        if not filters or not isinstance(filters, list):
            return False

        query = cls.query_exists_by(filters, params, **kwargs)
        async with cls._async_connection_context() as ctx:
            return await cls.perform_exists_by(ctx, query, **kwargs)

    #
    # Modification operations
    #

    @classmethod
    async def create(cls, data: Union[CreateSchemaType, Dict[str, Any]]) -> Optional['SqlModel']:
        if isinstance(data, dict):
            create_data = data
        else:
            create_data = data.dict(exclude_unset=True)

        if create_data:
            create_data = cls.prepare_for_create(create_data)

        async with cls._async_connection_context(begin_tx=True, autocommit=True) as ctx:
            if instance := await cls.perform_create(ctx, create_data):
                return await cls.construct_rela(ctx, instance)
        return None

    @classmethod
    async def update_by_id(cls, id_value: Any, data: Union[UpdateSchemaType, Dict[str, Any]]) -> Optional['SqlModel']:
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.dict(exclude_unset=True)

        if update_data:
            update_data = cls.prepare_for_update(update_data)

        async with cls._async_connection_context(begin_tx=True, autocommit=True) as ctx:
            if data := await cls.perform_update(ctx, update_data, id_value):
                if instance := await cls.construct(ctx, data):
                    return await cls.construct_rela(ctx, instance)
        return None

    async def update(self, data: Union[UpdateSchemaType, Dict[str, Any]]) -> bool:
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.dict(exclude_unset=True)

        if update_data:
            update_data = self.prepare_for_update(update_data)

        async with self._async_connection_context(begin_tx=True, autocommit=True) as ctx:
            if row := await self.perform_update(ctx, update_data, self.get_id_value()):
                await self.assign(row).reload_rela(ctx, set(update_data.keys()))
                return True

        return False

    @classmethod
    async def delete_by_id(cls, id_value: Any) -> bool:
        async with cls._async_connection_context(begin_tx=True, autocommit=True) as ctx:
            return await cls.perform_delete(ctx, id_value)

    async def delete(self) -> bool:
        async with self._async_connection_context(begin_tx=True, autocommit=True) as ctx:
            return await self.perform_delete(ctx, self.get_id_value())

    @classmethod
    def prepare_for_create(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        return data

    @classmethod
    def prepare_for_update(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        return data

    @classmethod
    def prepare_for_delete(cls, obj: 'SqlModel') -> 'SqlModel':
        return obj

    async def save(self, updated_fields: List[str] = None, **kwargs) -> bool:
        cols = self.get_columns()

        if updated_fields is not None and isinstance(updated_fields, Sequence):
            updated_fields = set(updated_fields)
            cols = [(col.name, col) for col in cols if self._get_field_by_column(col) in updated_fields]
            cols = ColumnCollection(columns=cols)
        else:
            updated_fields = set()

        col_values = self._get_column_values(cols, force_tuple=True)
        data = {k.name: v for k, v in zip(cols, col_values)}

        async with self._async_connection_context(begin_tx=True, autocommit=True) as ctx:
            res = await self.perform_save(ctx, data, updated_fields, **kwargs)
            await self.reload_rela(ctx, updated_fields, **kwargs)

        return len(res.keys()) > 0 if res else False

    async def load(self, field_names: List[str] = None) -> bool:
        async with self._async_connection_context() as ctx:
            return await self.perform_load(ctx, field_names)

    @classmethod
    async def save_all(cls, objects: List['SqlModel'], **kwargs) -> bool:
        async with cls._async_connection_context(begin_tx=True, autocommit=True) as ctx:
            return await cls.perform_save_all(ctx, objects, **kwargs)

    #
    # Query operations
    #

    @classmethod
    def query_get(cls, id_value: Any, **kwargs):
        return cls._get_helper(id_value, **kwargs)

    @classmethod
    def query_list(cls, filters: List[Any], sorting: List[Any],
                   skip: int = 0, limit: int = 0, params: Dict[str, Any] = None, **kwargs):
        query = cls.get_db_query(**kwargs).offset(skip if skip >= 0 else 0)
        if limit > 0:
            query = query.limit(limit)
        for f in filters:
            query = query.where(f)
        if filters and params:
            query = query.params(**params)
        for s in sorting:
            query = query.order_by(s)
        return query

    @classmethod
    def query_any(cls, indices: List[Any], **kwargs):
        return cls._get_any_helper(indices, **kwargs)

    # noinspection PyUnresolvedReferences
    @classmethod
    def query_count(cls, filters: Optional[List[Any]] = None, params: Dict[str, Any] = None, **kwargs):
        if filters:
            query = cls.get_db_query()
            for f in filters:
                query = query.where(f)
            if params:
                query = query.params(**params)
        else:
            query = cls.__table__

        return select([func.count(literal_column('1'))]).select_from(query.alias())

    @classmethod
    def query_exists(cls, id_value: Any, **kwargs):
        return cls._get_helper(id_value, query=exists(), **kwargs).select()

    @classmethod
    def query_exists_by(cls, filters: List[Any], params: Dict[str, Any] = None, **kwargs):
        query = exists(cls)

        for f in filters:
            query = query.where(f)
        if filters and params:
            query = query.params(**params)

        return query.select()

    #
    # Perform operations
    #

    @classmethod
    async def perform_get(cls, ctx: ContextData, query, **kwargs) -> Optional['SqlModel']:
        raise NotImplementedError

    @classmethod
    async def perform_list(cls, ctx: ContextData, query, **kwargs) -> List['SqlModel']:
        raise NotImplementedError

    @classmethod
    async def perform_any(cls, ctx: ContextData, query, **kwargs) -> List[Optional['SqlModel']]:
        raise NotImplementedError

    @classmethod
    async def perform_count(cls, ctx: ContextData, query, **kwargs) -> int:
        raise NotImplementedError

    @classmethod
    async def perform_exists(cls, ctx: ContextData, query, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    async def perform_exists_by(cls, ctx: ContextData, query, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    async def perform_create(cls, ctx: ContextData, data: Dict[str, Any]) -> Optional['SqlModel']:
        raise NotImplementedError

    @classmethod
    async def perform_update(
            cls, ctx: ContextData, data: Dict[str, Any], id_value: Any) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @classmethod
    async def perform_delete(cls, ctx: ContextData, id_value: Any) -> bool:
        raise NotImplementedError

    async def perform_save(
        self, ctx: ContextData, data: Dict[str, Any], updated_fields: Set[str], **kwargs) \
            -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    async def perform_load(self, ctx: ContextData, field_names: List[str] = None) -> bool:
        raise NotImplementedError

    @classmethod
    async def perform_save_all(cls, ctx: ContextData, objects: List['SqlModel'], **kwargs) -> bool:
        raise NotImplementedError

    #
    # Private
    #

    # noinspection PyUnresolvedReferences
    @classmethod
    def _get_id_columns(cls) -> ColumnCollection:
        return cls.__table__.primary_key.columns

    # noinspection PyTypeChecker
    def _get_column_values(
            self, columns: ColumnCollection, force_tuple: bool = False) -> Union[Any, Tuple[Any]]:
        rv = []
        for c in columns:
            rv.append(getattr(self, self._get_field_by_column(c)))
        return rv[0] if len(rv) == 1 and not force_tuple else tuple(rv)

    @classmethod
    def _get_field_by_column(cls, c: Column) -> str:
        raise NotImplementedError

    # noinspection PyUnresolvedReferences
    @classmethod
    def _get_fk_columns(cls, model) -> ColumnCollection:
        for fk in cls.__table__.foreign_keys:
            if model.__table__ == fk.constraint.referred_table:
                return fk.constraint.columns
        return ColumnCollection()

    @classmethod
    def _get_helper(cls, ident: Any, query=None, **kwargs):
        cls._check_abstract()
        if not isinstance(ident, (list, tuple, dict)):
            ident_ = [ident]
        else:
            ident_ = ident
        columns = cls._get_id_columns()
        if len(ident_) != len(columns):
            raise ValueError(
                f'Incorrect number of values as primary key: expected {len(columns)}, got {len(ident_)}.')

        clause = query if query is not None else cls.get_db_query(**kwargs)
        for i, c in enumerate(columns):
            try:
                val = ident_[i]
            except KeyError:
                val = ident_[cls._get_field_by_column(c)]
            clause = clause.where(c == val)
        return clause

    @classmethod
    def _get_any_helper(cls, indices: List[Any], query=None, **kwargs):
        cls._check_abstract()
        columns = cls._get_id_columns()
        clause = query if query is not None else cls.get_db_query(**kwargs)
        vals_clause = []

        for ident in indices:
            if not isinstance(ident, (list, tuple, dict)):
                ident_ = [ident]
            else:
                ident_ = ident

            if len(ident_) != len(columns):
                raise ValueError(
                    f'Incorrect number of values as primary key: expected {len(columns)}, got {len(ident_)}.')

            vals = []
            for i, c in enumerate(columns):
                try:
                    val = ident_[i]
                except KeyError:
                    val = ident_[cls._get_field_by_column(c)]
                vals.append(val)

            if len(vals) == 1:
                vals_clause.append(vals[0])
            elif len(vals) > 1:
                vals_clause.append((*vals,))

        if len(columns) == 1:
            clause = clause.where(columns[columns.keys()[0]].in_(vals_clause))
        elif len(columns) > 1:
            clause = clause.where(tuple_(*columns).in_(vals_clause))
        return clause

    @classmethod
    async def _get_from_orm_cache(cls, ctx: ContextData, indices: List[Any]) -> List[Optional['SqlModel']]:
        return [None for _ in indices]
