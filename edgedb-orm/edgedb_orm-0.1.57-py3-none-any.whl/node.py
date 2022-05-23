import typing as T
import re
from uuid import UUID
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
from fastapi.encoders import jsonable_encoder
import edgedb
from devtools import debug
from pydantic import BaseModel, PrivateAttr, Field

from .unset import is_unset
from .cache import CacheManager
from .execute import query as execute_query
from .batch import Batch
from .constants import random_str
from . import creating_strings
from .span import safe_span

InsertType = T.TypeVar("InsertType", bound=BaseModel)
PatchType = T.TypeVar("PatchType", bound=BaseModel)

ThisNodeType = T.TypeVar("ThisNodeType", bound="Node")

BaseModelType = T.TypeVar("BaseModelType", bound=BaseModel)

TempNodeType = T.TypeVar("TempNodeType", bound="Node")
if T.TYPE_CHECKING:
    from .resolver import Resolver

    TempResolverType = T.TypeVar("TempResolverType", bound=Resolver)
    ResolverType = T.TypeVar("ResolverType", bound=Resolver)


class NodeException(Exception):
    pass


def model_dict_to_str(
    *,
    d: dict,
    edgedb_conversion_map: T.Dict[str, T.Dict[str, str]],
    set_links_d: T.Dict[str, "Resolver"] = None,
    force_replace: bool = False,  # make this true for inserts
    set_strs: T.List[str] = None,
    error: bool = False,
) -> T.Tuple[str, T.Dict[str, T.Any]]:
    from .resolver import UpdateOperation

    field_strs: T.List[str] = []
    variables = {}
    for field_name, val in d.items():
        add_to_variables: bool = True
        type_cast_str = edgedb_conversion_map.get(field_name, {}).get("cast")
        if val is None:
            val = set()

        if not type_cast_str:
            # resolvers will come up here so ignore them
            if (set_links_d and field_name in set_links_d) or val == set():
                continue
            # if this is a resolver, it is fine... also what if it is none?
            if error:
                raise NodeException(
                    f"{field_name=}, {val=} not in {edgedb_conversion_map=}"
                )
            else:
                continue

        variable_name = f"{field_name}{random_str(10)}"
        # if enum, turn to str cast instead
        type_cast_str = re.sub(r"default::\w+", "std::str", type_cast_str)
        field_str = f"{field_name} := <{type_cast_str}>${variable_name}"
        if type_cast_str.endswith("::str") and (
            isinstance(val, dict) or isinstance(val, list)
        ):
            # for basemodel subfields that should go from dict to str
            val = json.dumps(jsonable_encoder(val))
        if type(val) is set:
            val = list(val)
            if "array<" not in type_cast_str:
                field_str = f"{field_name} := array_unpack(<array<{type_cast_str}>>${variable_name})"
                if len(val) == 0:
                    add_to_variables = False
                    field_str = f"{field_name} := {{}}"
        field_strs.append(field_str)
        if add_to_variables:
            variables[variable_name] = val
    if set_links_d:
        for field_name, resolver in set_links_d.items():
            update_operation_str = resolver.update_operation_str
            if force_replace:
                update_operation_str = UpdateOperation.REPLACE.value
            if not update_operation_str:
                raise NodeException(
                    f"Update resolver for {field_name} does not have an update operation."
                )
            field_str = (
                f"{field_name} {update_operation_str}"
                f" (SELECT DETACHED {resolver._model_name}{resolver.all_filters_str()})"
            )
            field_strs.append(field_str)
            for variable_name, variable_value in resolver._query_variables.items():
                if variable_name in variables:
                    raise NodeException(
                        f"Query variable {variable_name} for update resolver {field_name} "
                        f"already exists in variables {variables}."
                    )
                variables[variable_name] = variable_value
    if set_strs:
        field_strs.extend(set_strs)
    s = f'{{ {", ".join(field_strs)} }}'
    return s, variables


def make_set_links_d(
    model: BaseModel, model_d: dict, default_replace: bool = False
) -> T.Dict[str, "ResolverType"]:
    """mutates model_d and returns set links d"""
    from .resolver import Resolver, UpdateOperation

    set_links_d = {}
    for field_name in model.__fields__.keys():
        val = getattr(model, field_name)
        if isinstance(val, Resolver):
            if not val._update_operation and default_replace:
                val.update_operation(UpdateOperation.REPLACE)
            set_links_d[field_name] = val
            if field_name in model_d:
                del model_d[field_name]
    return set_links_d


def basemodel_to_str(
    model: BaseModelType,
    default_replace: bool = False,
    fields_to_exclude: T.Set[str] = None,
    force_replace: bool = False,
) -> T.Tuple[str, T.Dict[str, T.Any]]:
    # should exclude_none = True?
    # model_d = model.dict(exclude_none=True, exclude=fields_to_exclude)
    # TODO is this right?
    model_d = model.dict(exclude=fields_to_exclude)

    set_links_d = make_set_links_d(
        model=model, model_d=model_d, default_replace=default_replace
    )

    return model_dict_to_str(
        d=model_d,
        edgedb_conversion_map=model._edgedb_conversion_map,
        set_links_d=set_links_d,
        force_replace=force_replace,
    )


def resolver_equal_or_better(
    resolver_a: "ResolverType", resolver_b: "ResolverType"
) -> bool:
    # TODO must compare variables as well
    a_nested_vars = resolver_a._get_nested_query_variables()
    b_nested_vars = resolver_b._get_nested_query_variables()
    if a_nested_vars != b_nested_vars:
        # if b has any vars a does not have
        if len(set(b_nested_vars.keys()) - set(a_nested_vars.keys())) > 0:
            return False
        for k, v in a_nested_vars.items():
            if k not in b_nested_vars:
                # continue because this will be picked up in the filters if it is important
                continue
            if b_nested_vars[k] != v:
                print(
                    f"{k=}, {b_nested_vars[k]=} is not equal to {v=} so returning false"
                )
                return False

    if resolver_a.to_str() == resolver_b.to_str():
        return True
    if resolver_a.all_filters_str() != resolver_b.all_filters_str():
        return False
    # check if rez b has appendix fields or other fields to return that A does not
    if len(resolver_b.get_fields_to_return() - resolver_a.get_fields_to_return()) > 0:
        return False
    # now go to nesteds
    for (
        nested_resolver_name_b,
        nested_resolver_b,
    ) in resolver_b._nested_resolvers.items():
        nested_resolver_a = resolver_a._nested_resolvers.get(nested_resolver_name_b)
        if not nested_resolver_a:
            print(
                f"{nested_resolver_name_b} is not in the cached {resolver_a._model_name} resolver"
            )
            return False
        if not resolver_equal_or_better(nested_resolver_a, nested_resolver_b):
            return False
    return True


class Node(BaseModel, T.Generic[InsertType, PatchType]):
    id: UUID = Field(..., allow_mutation=False)

    _cache: CacheManager = PrivateAttr(default_factory=CacheManager)
    _used_resolver: "ResolverType" = PrivateAttr(None)
    _original_dict: dict = PrivateAttr(None)
    _deleted: bool = PrivateAttr(None)

    _edgedb_conversion_map: T.ClassVar[T.Dict[str, T.Dict[str, str]]]
    _link_conversion_map: T.ClassVar[T.Dict[str, T.Dict[str, str]]]
    _computed_properties: T.ClassVar[T.Set[str]]
    _appendix_properties: T.ClassVar[T.Set[str]]
    _basemodel_properties: T.ClassVar[T.Set[str]]

    _extra: dict = PrivateAttr(default=dict())

    __updated_fields__: T.Set[str] = PrivateAttr(default=set())

    def __setattr__(self, key, value):
        self.__updated_fields__.add(key)
        if key in self._appendix_properties:
            # TODO is this the desired effect?
            #  Probably, if you set an appendix field, add it to fields returned in future
            self._used_resolver.include_fields(key)
            k = f"{key}_"
            if k in self.__fields__.keys():
                key = k
        return super().__setattr__(key, value)

    def updated_fields(self, *updated_fields: str) -> None:
        self.__updated_fields__.update(updated_fields)

    def _clear_updated_fields(self) -> None:
        self.__updated_fields__ = set()

    @property
    def extra(self) -> dict:
        return self._extra

    class Config:
        validate_assignment = True
        underscore_attrs_are_private = False

    class GraphORM:
        model_name: str = None
        client: edgedb.AsyncIOClient
        exclusive_fields: T.Set[str] = None
        resolver_type: T.ClassVar[T.Type["ResolverType"]]
        updatable_fields: T.ClassVar[T.Set[str]] = set()

    @classmethod
    def get_aliases(cls) -> T.Set[str]:
        return {field.alias for field in cls.__fields__.values()}

    def __eq__(self, other: TempNodeType) -> bool:
        if not isinstance(other, Node):
            return False
        return f"{hash(self)}{self.json()}" == f"{hash(other)}{other.json()}"

    def __hash__(self) -> int:
        return hash(f"{self.__class__.__name__}{self.json()}")

    def to_resolver(self) -> "ResolverType":
        return self._used_resolver.__class__().filter(
            filter_str=".id = <uuid>$id", variables={"id": self.id}
        )

    @classmethod
    def to_resolver_many(
        cls: T.Type[ThisNodeType], nodes: T.List[ThisNodeType]
    ) -> "ResolverType":
        return cls.GraphORM.resolver_type().filter(
            ".id in array_unpack(<array<uuid>>$ids)",
            variables={"ids": [n.id for n in nodes]},
        )

    @property
    def cache(self) -> CacheManager:
        return self._cache

    @classmethod
    @property
    def db_client(cls) -> edgedb.AsyncIOClient:
        return cls.GraphORM.client

    def __repr__(self) -> str:
        r = super().__repr__()
        r = f"{r}, cache: {repr(self.cache)}" if not self.cache.is_empty() else r
        return r

    """CACHE"""

    async def resolve(
        self,
        edge_name: str,
        edge_resolver: "TempResolverType",
        refresh: bool = False,
        force_use_stale: bool = False,
        print_forced_refresh: bool = True,
    ) -> T.Optional[T.Union[TempNodeType, T.List[TempNodeType]]]:
        """return await self.resolve(
            name="artist", resolver=resolver, refresh=refresh, use_stale=use_stale
        )
        DID NOT INCLUDE STRICT, maybe will need it but for now i do not"""
        if refresh:
            self.cache.remove(edge_name)
        if edge_cache := self.cache.get(edge_name):
            if force_use_stale:
                return edge_cache.val
            if not resolver_equal_or_better(edge_cache.resolver, edge_resolver):
                if print_forced_refresh:
                    print(
                        f"resolvers are different so removing {edge_name} from the cache, old: {edge_cache.resolver.to_str()}, new: {edge_resolver.to_str()}"
                    )
                self.cache.remove(edge_name)
        if not self.cache.exists(edge_name):
            self.used_resolver._nested_resolvers[edge_name] = edge_resolver
            self._used_resolver.clear_top_level_filters_and_variables()
            obj = await self.used_resolver.get(id=self.id)
            self.cache.replace(key=edge_name, cache=obj.cache.get(edge_name))
        return self.cache.get_val(edge_name)

    """CRUDS"""

    @property
    def used_resolver(self) -> "ResolverType":
        return self._used_resolver

    @staticmethod
    def validate_upsert_fields(
        upsert_given_conflict_on: str = None,
        return_conflicting_model_on: str = None,
        custom_on_conflict_str: str = None,
    ) -> None:
        if custom_on_conflict_str:
            if return_conflicting_model_on or upsert_given_conflict_on:
                raise NodeException(
                    "You cannot give a custom conflict string with other conflict inputs."
                )
        if return_conflicting_model_on and upsert_given_conflict_on:
            raise NodeException(
                "You cannot both suppress a conflict and upsert given a conflict."
            )

    def build_insert_str(
        self,
        use_all_fields: bool = False,  # true for FOR cause some objects might have null values while some do not
        upsert_given_conflict_on: str = None,
        return_conflicting_model_on: str = None,
        custom_on_conflict_str: str = None,
    ) -> str:
        ...

    @classmethod
    async def add(
        cls: T.Type[ThisNodeType],
        insert: InsertType,
        given_resolver: "ResolverType" = None,
        batch: Batch = None,
        given_client: edgedb.AsyncIOClient = None,
        upsert_given_conflict_on: str = None,
        return_conflicting_model_on: str = None,
        custom_on_conflict_str: str = None,
    ) -> T.Optional[ThisNodeType]:
        """Turn insert into a string with variables"""
        if not given_resolver:
            given_resolver = cls.GraphORM.resolver_type()
        cls.validate_upsert_fields(
            upsert_given_conflict_on=upsert_given_conflict_on,
            return_conflicting_model_on=return_conflicting_model_on,
            custom_on_conflict_str=custom_on_conflict_str,
        )
        # I think default_replace=True is correct here. Your intention is to make sure these links are SET, not updated
        # if your intention is for them to update on upsert, then add ADD to the resolver
        s, variables = basemodel_to_str(
            insert, default_replace=True, force_replace=True
        )
        insert_str = f"INSERT {cls._model_name} {s}"
        conflict_str = ""
        if custom_on_conflict_str:
            conflict_str = custom_on_conflict_str
        elif upsert_given_conflict_on:
            # replace s and variables
            # insert_dict = insert.dict(exclude_none=True)
            # TODO again for exclude_none is this right?
            insert_dict = insert.dict()
            fields_to_exclude = set(insert_dict.keys()) - cls.GraphORM.updatable_fields
            update_s, update_variables = basemodel_to_str(
                insert, default_replace=True, fields_to_exclude=fields_to_exclude
            )
            variables.update(update_variables)
            conflict_str = f"UNLESS CONFLICT ON .{upsert_given_conflict_on} ELSE (UPDATE {cls._model_name} SET {update_s})"
        elif return_conflicting_model_on:
            conflict_str = f"UNLESS CONFLICT ON .{return_conflicting_model_on} ELSE (SELECT {cls._model_name})"
        if conflict_str:
            insert_str += f" {conflict_str}"
        if batch:
            batch.add(line=insert_str, variables={**variables})
            return None
        select_str = f"SELECT model {given_resolver.to_str()}"
        add_s = f"WITH model := ({insert_str}) {select_str}"
        with safe_span(op=f"edgedb.add.{cls._model_name}"):
            raw_d = await execute_query(
                client=given_client or cls.db_client,
                query_str=add_s,
                variables=variables,
                only_one=True,
            )
        with safe_span(op=f"parse.{cls._model_name}"):
            return given_resolver.parse_nested_obj(raw_d)

    @classmethod
    async def add_many(
        cls: T.Type[ThisNodeType],
        inserts: T.List[InsertType],
        edge_filter_strs: T.List[str] = None,
        given_resolver: "ResolverType" = None,
        given_client: edgedb.AsyncIOClient = None,
        upsert_given_conflict_on: str = None,
        return_conflicting_model_on: str = None,
        custom_on_conflict_str: str = None,
    ) -> T.List[ThisNodeType]:
        """This returns in no specific order"""
        if not given_resolver:
            given_resolver = cls.GraphORM.resolver_type()
        if not edge_filter_strs:
            edge_filter_strs = []
        cls.validate_upsert_fields(
            upsert_given_conflict_on=upsert_given_conflict_on,
            return_conflicting_model_on=return_conflicting_model_on,
            custom_on_conflict_str=custom_on_conflict_str,
        )
        if not inserts:
            return list()
        insert_str = creating_strings.insert_str_from_cls(
            insert_cls=inserts[0].__class__,
            node_cls=cls,
            edge_filter_strs=edge_filter_strs,
            upsert_given_conflict_on=upsert_given_conflict_on,
            return_conflicting_model_on=return_conflicting_model_on,
            custom_on_conflict_str=custom_on_conflict_str,
        )
        full_insert_str = f"""
with
    raw_data := <json>$data,
for item in json_array_unpack(raw_data) union ({insert_str}) {given_resolver.to_str()}
        """
        print(f"{full_insert_str=}")
        data: T.List[T.Dict[str, T.Any]] = []
        for insert in inserts:
            d = insert.dict(exclude_none=True)
            # TODO for bulk adding, best to exclude
            # d = insert.dict()
            # if the cast says they should be strings and they are not, turn them into json
            for field_name, value in d.items():
                if cast := cls._edgedb_conversion_map.get(field_name, {}).get("cast"):
                    if (
                        cast.endswith("::str")
                        and not isinstance(value, str)
                        and not type(value) in [set]
                    ):
                        # if ITERABLE of strs, ignore. For now just SET, cause what if list of objs
                        d[field_name] = json.dumps(jsonable_encoder(value))
            # get fields that are LINKS
            for link_name in cls._link_conversion_map.keys():
                if link_resolver := getattr(insert, link_name, None):
                    d[link_name] = {**link_resolver._query_variables}
            data.append(d)
        data_json = json.dumps(jsonable_encoder(data))
        len_inserts = len(inserts)
        with safe_span(
            op=f"edgedb.add_many.{cls._model_name}", description=f"{len_inserts=}"
        ):
            raw_d = await execute_query(
                client=given_client or cls.db_client,
                query_str=full_insert_str,
                variables={"data": data_json},
            )
        with safe_span(op=f"parse.{cls._model_name}", description=f"{raw_d=}"):
            return [given_resolver.parse_nested_obj(d) for d in raw_d]

    @classmethod
    async def add_many_old(
        cls: T.Type[ThisNodeType],
        inserts: T.List[InsertType],
        given_resolver: "ResolverType" = None,
        given_client: edgedb.AsyncIOClient = None,
    ) -> T.List[ThisNodeType]:
        """This appears to have a max limit of something between 30 and 50, so must break it up"""
        if not given_resolver:
            given_resolver = cls.GraphORM.resolver_type()
        insert_strs: T.List[str] = []
        variables = {}
        for i, insert in enumerate(inserts):
            insert_str, insert_variables = basemodel_to_str(model=insert)
            insert_strs.append(insert_str)
            variables.update(insert_variables)
        insert_lines: T.List[str] = []
        model_name = cls._model_name
        model_enumerated_names: T.List[str] = []
        for i, insert_str in enumerate(insert_strs):
            model_enumerated_name = f"model_{i}"
            insert_lines.append(
                f"{model_enumerated_name} := (INSERT {model_name} {insert_str})"
            )
            model_enumerated_names.append(model_enumerated_name)
        insert_lines.append(f'models := ({" UNION ".join(model_enumerated_names)})')
        add_many_s = (
            f'WITH {", ".join(insert_lines)} SELECT models {given_resolver.to_str()}'
        )
        raw_d = await execute_query(
            client=given_client or cls.db_client,
            query_str=add_many_s,
            variables=variables,
        )
        return [given_resolver.parse_nested_obj(d) for d in raw_d]

    async def delete(
        self,
        given_resolver: "ResolverType" = None,
        batch: Batch = None,
        given_client: edgedb.AsyncIOClient = None,
    ) -> None:
        if not given_resolver:
            given_resolver = self._used_resolver
        given_resolver.clear_top_level_filters_and_variables()
        given_resolver.filter(filter_str=".id = <uuid>$id", variables={"id": self.id})
        if batch:
            batch.add(
                line=given_resolver.inner_delete_str(),
                variables=given_resolver._get_nested_query_variables(),
            )
            return
        with safe_span(op=f"edgedb.delete.{self._model_name}"):
            raw_d = await execute_query(
                client=given_client or self.db_client,
                query_str=given_resolver.full_delete_str(),
                variables=given_resolver._get_nested_query_variables(),
                only_one=True,
            )
        if not raw_d:
            raise NodeException(
                f"No delete for {self._model_name}: {self.id} was registered."
            )
        with safe_span(op=f"parse.{self._model_name}"):
            node = given_resolver.parse_nested_obj(raw_d)
        node._deleted = True
        self.hydrate(new_node=node)

    @classmethod
    async def delete_many(
        cls: T.Type[ThisNodeType],
        models: T.List[ThisNodeType],
        given_resolver: "ResolverType" = None,
    ) -> None:
        if not given_resolver:
            given_resolver = cls.GraphORM.resolver_type()
        given_resolver.clear_top_level_filters_and_variables()
        given_resolver.filter(
            filter_str=".id in array_unpack(<array<uuid>>$ids)",
            variables={"ids": [model.id for model in models]},
        )
        len_models = len(models)
        with safe_span(
            op=f"edgedb.delete_many.{cls._model_name}", description=f"{len_models=}"
        ):
            raw_d = await execute_query(
                client=cls.db_client,
                query_str=given_resolver.full_delete_str(),
                variables=given_resolver._get_nested_query_variables(),
            )
        with safe_span(op=f"parse.{cls._model_name}", description=f"{len(raw_d)=}"):
            new_nodes = [given_resolver.parse_nested_obj(d) for d in raw_d]
        models_by_id: T.Dict[str, ThisNodeType] = {model.id: model for model in models}
        for new_node in new_nodes:
            new_node._deleted = True
            models_by_id[new_node.id].hydrate(new_node=new_node)

    @classmethod
    async def delete_from_filtered_resolver(
        cls,
        filtered_resolver: "ResolverType",
        batch: Batch = None,
        given_client: edgedb.AsyncIOClient = None,
    ) -> T.Optional[T.List[ThisNodeType]]:
        if batch:
            batch.add(
                line=filtered_resolver.inner_delete_str(),
                variables=filtered_resolver._get_nested_query_variables(),
            )
            return
        with safe_span(op=f"edgedb.delete_from_filtered_resolver.{cls._model_name}"):
            raw_d = await execute_query(
                client=given_client or cls.db_client,
                query_str=filtered_resolver.full_delete_str(),
                variables=filtered_resolver._get_nested_query_variables(),
                only_one=False,
            )
        with safe_span(op=f"parse.{cls._model_name}", description=f"{len(raw_d)=}"):
            nodes = [filtered_resolver.parse_nested_obj(d) for d in raw_d]
        for node in nodes:
            node._deleted = True
        return nodes

    @classmethod
    def build_update_d_from_patch(cls, patch: PatchType) -> dict:
        update_d = {}
        for field in patch.__fields__.keys():
            val = getattr(patch, field)
            if not is_unset(val):
                if val is None:
                    val = set()
                elif isinstance(val, BaseModel):
                    val = val.json()
                update_d[field] = val
        return update_d

    def build_update_d(self) -> dict:
        fields_to_update = self.__updated_fields__ & self.GraphORM.updatable_fields
        update_d = {}
        for field in fields_to_update:
            val = getattr(self, field)
            if val is None:
                val = set()
            elif isinstance(val, BaseModel):
                val = val.json()
            update_d[field] = val
        return update_d

    def get_update_d_old(self) -> dict:
        """DEP. Keep incase new one ^'build_update_d' is not good"""
        # for appendix properties
        # if you want to edit an appendix field, you must request it
        current_d = {**self.extra, **self.dict()}
        for field, val in current_d.items():
            print(f"{field=}, {val=}")
            if (
                field in self._basemodel_properties
                and field in self.GraphORM.updatable_fields
                and isinstance(getattr(self, field, None), BaseModel)
            ):
                current_d[field] = getattr(self, field).json()
        original_d = self._original_dict
        unset_key = "_UNSET_12398120"
        update_d = {}
        for field_name in self.GraphORM.updatable_fields:
            current_val = current_d.get(field_name, unset_key)
            original_val = original_d.get(field_name, unset_key)
            if current_val != original_val:
                if current_val != unset_key:
                    # if current val is not unset -> always set
                    print(f"{current_val=}, {original_val=}")
                    if current_val is not None:
                        if (
                            isinstance(current_val, datetime)
                            and current_val.isoformat() == original_val
                        ):
                            continue
                        else:
                            if isinstance(current_val, datetime):
                                print(
                                    f"datetimes diff for update: {current_val.isoformat()=}, {original_val=}"
                                )
                            update_d[field_name] = current_val
                    else:
                        update_d[field_name] = set()
                else:
                    # current val is UNSET but original val is not
                    update_d[field_name] = set()
        return update_d

    @classmethod
    async def _update(
        cls: T.Type[ThisNodeType],
        resolver: "ResolverType",
        update_d: dict,
        set_strs: T.List[str] = None,
        set_links_d: T.Dict[str, "Resolver"] = None,
        batch: Batch = None,
        given_client: edgedb.AsyncIOClient = None,
        only_one: bool = True,
    ) -> T.Optional[T.Union[ThisNodeType, T.List[ThisNodeType]]]:
        s, variables = model_dict_to_str(
            d=update_d,
            edgedb_conversion_map=cls._edgedb_conversion_map,
            set_links_d=set_links_d,
            set_strs=set_strs,
        )

        resolver.validate_against_query_variables(variables)
        update_inner_str = f"UPDATE {cls._model_name} {resolver._filter_str} SET {s}"

        variables_to_use = {**resolver._get_nested_query_variables(), **variables}

        if batch:
            batch.add(line=update_inner_str, variables=variables_to_use)
            return None

        update_s = (
            f"WITH model := ({update_inner_str}) "
            f"SELECT model {resolver.to_str(include_filters=False)}"
        )

        with safe_span(op=f"edgedb.update.{cls._model_name}"):
            raw_d = await execute_query(
                client=given_client or cls.db_client,
                query_str=update_s,
                variables=variables_to_use,
                only_one=only_one,
            )
        if not raw_d:
            raise NodeException(f"No update for {cls._model_name} was registered.")
        with safe_span(op=f"parse.{cls._model_name}"):
            if only_one:
                return resolver.parse_nested_obj(raw_d)
            else:
                return [resolver.parse_nested_obj(d) for d in raw_d]

    @classmethod
    async def update_from_patch(
        cls: T.Type[ThisNodeType],
        patch: PatchType,
        resolver_with_filter: "ResolverType",
        set_strs: T.List[str] = None,
        only_one: bool = True,
        update_last_updated: bool = False,
        batch: Batch = None,
        given_client: edgedb.AsyncIOClient = None,
    ) -> T.Optional[T.Union[ThisNodeType, T.List[ThisNodeType]]]:
        if update_last_updated:
            if is_unset(getattr(patch, "last_updated", None)):
                patch.last_updated = datetime.now(tz=ZoneInfo("America/New_York"))
        update_d = cls.build_update_d_from_patch(patch=patch)
        set_links_d = make_set_links_d(model=patch, model_d=update_d)
        if not update_d and not set_links_d:
            raise NodeException("No update registered.")
        node_or_nodes = await cls._update(
            resolver=resolver_with_filter,
            update_d=update_d,
            set_strs=set_strs,
            set_links_d=set_links_d,
            batch=batch,
            given_client=given_client,
            only_one=only_one,
        )
        if batch:
            return None
        return node_or_nodes

    async def update(
        self,
        given_resolver: "ResolverType" = None,
        error_if_no_update: bool = False,
        set_links_d: T.Dict[str, "Resolver"] = None,
        batch: Batch = None,
        given_client: edgedb.AsyncIOClient = None,
    ) -> None:
        """set_links_d -> {people_i_follow += (select Person filter .first_name = <str>first_name)}"""
        if not given_resolver:
            given_resolver = self._used_resolver
        update_d = self.build_update_d()
        if not update_d:
            message = f"No update registered for {self.id=}."
            if error_if_no_update:
                raise NodeException(message)
            else:
                print(message)
            return

        given_resolver.clear_top_level_filters_and_variables()
        given_resolver.filter(filter_str=".id = <uuid>$id", variables={"id": self.id})
        node = await self._update(
            resolver=given_resolver,
            update_d=update_d,
            set_links_d=set_links_d,
            batch=batch,
            given_client=given_client,
        )
        if batch:
            return None
        self.hydrate(new_node=node)

    @classmethod
    @property
    def _model_name(cls) -> str:
        model_name = getattr(cls.GraphORM, "model_name", None)
        if model_name is None:
            model_name = cls.__name__
        return model_name

    @classmethod
    @property
    def _exclusive_fields(cls) -> T.Set[str]:
        exclusive_fields = getattr(cls.GraphORM, "exclusive_fields", set())
        exclusive_fields.add("id")
        return exclusive_fields

    def hydrate(
        self, new_node: ThisNodeType, clear_updated_fields: bool = True
    ) -> None:
        """Turns this node into the new node"""
        if clear_updated_fields:
            self._clear_updated_fields()
        for field_name in new_node.__fields__.keys():
            new_field = getattr(new_node, field_name)
            old_field = getattr(self, field_name)
            if new_field != old_field:
                setattr(self, field_name, getattr(new_node, field_name))
        for private_attr_name in new_node.__private_attributes__.keys():
            setattr(self, private_attr_name, getattr(new_node, private_attr_name))

    async def refresh(self: ThisNodeType) -> None:
        if self._deleted:
            raise NodeException("Node is already deleted.")
        self._used_resolver.clear_top_level_filters_and_variables()
        new_node = await self._used_resolver.get(id=self.id)
        self.hydrate(new_node=new_node)
