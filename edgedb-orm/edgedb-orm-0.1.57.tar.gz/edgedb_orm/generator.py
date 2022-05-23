import json
import re
import typing as T
from enum import Enum
import os
from pathlib import Path
from black import format_str, FileMode
import edgedb
from pydantic import BaseModel, parse_raw_as
from devtools import debug
from .introspection import (
    introspect_objects,
    introspect_scalars,
    ObjectType,
    ScalarType,
    Link,
    Property,
    Cardinality,
)
from .enums import PropertyCardinality


class DBVendor(str, Enum):
    edgedb = "edgedb"


class TLSSecurity(str, Enum):
    insecure = "insecure"


class PropertyConfig(BaseModel):
    module_path: str
    module_name: str
    validate_as_basemodel: bool = True
    cardinality: PropertyCardinality = PropertyCardinality.ONE


class NodeConfig(BaseModel):
    module_path: str = None
    appendix_properties: T.List[str] = []
    basemodel_properties: T.Dict[str, PropertyConfig] = {}


class DBConfig(BaseModel):
    vendor: DBVendor
    host: str
    password: str
    port: int = 5656
    tls_security: TLSSecurity
    copy_config: str = None
    hydrate: bool = False
    nodes: T.Dict[str, NodeConfig] = dict()


PATH_TO_MODULE = "edgedb_orm"
DEFAULT_INDENT = "    "
CONFIG_NAME = "GraphORM"


class GeneratorException(Exception):
    pass


def indent_lines(s: str, indent: str = DEFAULT_INDENT) -> str:
    chunks = s.split("\n")
    return indent + f"\n{indent}".join(chunks)


def imports(enums_module: str) -> str:
    lines = [
        "from __future__ import annotations",
        "import typing as T",
        "from enum import Enum",
        "from datetime import datetime, date, timedelta",
        "from uuid import UUID",
        "from decimal import Decimal",
        "from edgedb import RelativeDuration, AsyncIOClient, create_async_client",
        "from pydantic import BaseModel, Field, PrivateAttr, validator",
        f"from {PATH_TO_MODULE} import Node, Resolver, NodeException, ResolverException, UpdateOperation, Batch, Unset, ComputedPropertyException, AppendixPropertyException, is_unset, from_str, enum_from_str, BasePatch, FilterConnector",
        f"from .{enums_module} import *",
        'EdgeResolverType = T.TypeVar("EdgeResolverType", bound=Resolver)',
    ]
    return "\n".join(lines)


def build_enum_imports() -> str:
    lines = ["from enum import Enum"]
    return "\n".join(lines)


async def build_enums(client: edgedb.AsyncIOClient, include_strawberry: bool) -> str:
    scalar_types = await introspect_scalars(client)
    enum_strs: T.List[str] = []
    enum_names: T.List[str] = []
    for scalar in scalar_types:
        if not scalar.enum_values:
            continue
        enum_value_strs: T.List[str] = [f'{e} = "{e}"' for e in scalar.enum_values]
        enum_value_str = "\n".join(enum_value_strs)
        s = f"class {scalar.node_name}(str, Enum):\n{indent_lines(enum_value_str)}"
        enum_strs.append(s)
        enum_names.append(scalar.node_name)
    if include_strawberry:
        straw_enums_str = "\n".join(
            [f"{enum_name} = strawberry.enum({enum_name})" for enum_name in enum_names]
        )
        straw_lines = [
            "import strawberry",
            f"class Strawberry:\n{indent_lines(straw_enums_str)}",
        ]
        enum_strs.extend(straw_lines)
    return "\n".join(enum_strs)


def build_node_link_function_str(link: Link) -> str:
    link_resolver_name = f"{link.target.model_name}Resolver"
    return f"""
async def {link.name}(
    self,
    resolver: {link_resolver_name} = None,
    refresh: bool = False,
    force_use_stale: bool = False,
) -> {link.type_str}:
    return await self.resolve(
        edge_name="{link.name}",
        edge_resolver=resolver or {link_resolver_name}(),
        refresh=refresh,
        force_use_stale=force_use_stale,
    )
    """


def build_resolver_link_function_str(node_resolver_name: str, link: Link) -> str:
    link_resolver_name = f"{link.target.model_name}Resolver"
    return f"""
def {link.name}(self, _: T.Optional[{link_resolver_name}] = None, /) -> {node_resolver_name}:
    if "{link.name}" in self._nested_resolvers:
        raise ResolverException("A resolver for `{link.name}` has already been provided.")
    self._nested_resolvers["{link.name}"] = _ or {link_resolver_name}()
    return self
    """


def build_get_functions_str(node_name: str, exclusive_field_names: T.Set[str]) -> str:
    exclusive_field_names = sorted(list(exclusive_field_names))
    params_fields_str = ", ".join(
        [f"{f}: T.Optional[T.Any] = None" for f in exclusive_field_names]
    )
    dict_fields_str = ", ".join([f'"{f}": {f}' for f in exclusive_field_names])
    get_str = f"""
async def get(self, given_client: AsyncIOClient = None, {params_fields_str}) -> T.Optional[{node_name}]:
    return await super().get(given_client=given_client, **{{{dict_fields_str}}})
    """
    gerror_str = f"""
async def gerror(self, given_client: AsyncIOClient = None, {params_fields_str}) -> {node_name}:
    return await super().gerror(given_client=given_client, **{{{dict_fields_str}}})
    """
    return f"{get_str}\n{gerror_str}"


def build_filter_functions_str(node_name: str, conversion_map: T.Dict[str, dict]):
    field_names = sorted(conversion_map.keys())
    params_fields_str = ", ".join(
        [f"{f}: T.Optional[T.Any] = None" for f in field_names]
    )
    dict_fields_str = ", ".join([f'"{f}": {f}' for f in field_names])
    filter_by_str = f"""
def filter_by(self, filter_connector: FilterConnector = None, {params_fields_str}) -> {node_name}Resolver:
    return super().filter_by(connector=filter_connector, **{{{dict_fields_str}}})
    """
    # now for filter in
    params_fields_lst_str = ", ".join(
        [f"{f}: T.Optional[T.List[T.Any]] = None" for f in field_names]
    )
    filter_in_str = f"""
def filter_in(self, filter_connector: FilterConnector = None, {params_fields_lst_str}) -> {node_name}Resolver:
    return super().filter_in(connector=filter_connector, **{{{dict_fields_str}}})
    """
    return f"{filter_by_str}\n{filter_in_str}"


def build_update_function_str(node_resolver_name: str, links: T.List[Link]) -> str:
    link_strs: T.List[str] = []
    link_names: T.List[str] = []
    for link in links:
        if link.readonly:
            continue
        link_strs.append(
            f"{link.name}: T.Optional[{link.target.model_name}Resolver] = None"
        )
        link_names.append(link.name)
    link_params_str = ", ".join(link_strs)
    return f"""
async def update(
    self,
    given_resolver: {node_resolver_name} = None,
    error_if_no_update: bool = False,
    batch: Batch = None,
    given_client: AsyncIOClient = None,
    {link_params_str}
) -> None:
    set_links_d = {{{", ".join([f'"{link_name}": {link_name}' for link_name in link_names])}}}
    set_links_d = {{key: val for key, val in set_links_d.items() if val is not None}}

    return await super().update(
        given_resolver=given_resolver,
        error_if_no_update=error_if_no_update,
        set_links_d=set_links_d,
        batch=batch,
        given_client=given_client
    )
    """


def add_quotes(lst: T.Iterable[str]) -> T.Iterable[str]:
    return [f'"{o}"' for o in lst]


def build_orm_config(
    model_name: str, updatable_fields: T.Set[str], exclusive_fields: T.Set[str]
) -> str:
    return f"""
class {CONFIG_NAME}:
    model_name = "{model_name}"
    client = client
    updatable_fields: T.Set[str] = {{{', '.join(add_quotes(sorted(list(updatable_fields))))}}}
    exclusive_fields: T.Set[str] = {{{', '.join(add_quotes(sorted(list(exclusive_fields))))}}}
    """


def stringify_dict(
    d: T.Union[T.Dict[str, str], str], stringify_value: bool = True
) -> str:
    if type(d) is not dict:
        s = f"{d}"
        if type(d) is not bool:
            if stringify_value:
                s = f'"{s}"'
        return s
    inner = [
        f'"{k}":{stringify_dict(v, stringify_value=stringify_value)}'
        for k, v in d.items()
    ]
    return f"{{{','.join(inner)}}}"


def stringify_set(s: T.Set[str]) -> str:
    if not s:
        return "set()"
    s_sorted = sorted(list(s))
    strs: T.List[str] = [f'"{i}"' for i in s_sorted]
    return "{" + ",".join(strs) + "}"


def edgedb_conversion_type_from_prop(prop: Property) -> str:
    """
    s = prop.target.name
    pattern = r"default::\w+"
    s = re.sub(pattern, "std::str", s)
    return s
    """
    return prop.target.name


def build_validator_module_imports(db_config: DBConfig) -> str:
    if not db_config.nodes:
        return ""
    node_configs = db_config.nodes.values()
    from_str_import_strs: T.List[str] = []
    for node_config in node_configs:
        for prop_name, prop_config in node_config.basemodel_properties.items():
            from_str_import_strs.append(
                f"from {prop_config.module_path} import {prop_config.module_name}"
            )
    return "\n".join(sorted(list(set(from_str_import_strs))))


def build_from_str_validator_str(node_config: T.Optional[NodeConfig]) -> str:
    if not node_config:
        return ""
    field_name_strs: T.List[str] = []
    for field_name, props_config in node_config.basemodel_properties.items():
        if props_config.validate_as_basemodel is False:
            continue
        key = field_name
        if field_name in node_config.appendix_properties:
            key += "_"
        field_name_strs.append(f'"{key}"')
    if not field_name_strs:
        return ""
    return f"""
_from_str = validator({", ".join(field_name_strs)}, pre=True, allow_reuse=True)(from_str)
    """


def remove_falsies(lst: list) -> list:
    return [i for i in lst if i]


def build_node_and_resolver(
    object_type: ObjectType,
    node_config: T.Optional[NodeConfig],
    edge_resolver_map_strs: T.List[str],
    hydrate: bool,
    dehydrate: bool,
) -> str:
    # need to sort props and links by required, exclusive, no default, rest
    object_type.properties.sort(
        key=lambda x: f"{not x.is_computed}-{x.required}-{x.is_exclusive}-{x.default}",
        reverse=True,
    )
    object_type.links.sort(
        key=lambda x: f"{not x.is_computed}-{x.required}-{x.is_exclusive}-{x.default}",
        reverse=True,
    )
    # start with the properties
    node_resolver_name = f"{object_type.node_name}Resolver"
    property_strs: T.List[str] = []
    insert_property_strs: T.List[str] = []
    patch_property_strs: T.List[str] = []
    updatable_fields: T.Set[str] = set()
    exclusive_fields: T.Set[str] = set()

    node_edgedb_conversion_map: T.Dict[str, T.Dict[str, str]] = {}
    insert_edgedb_conversion_map: T.Dict[str, T.Dict[str, str]] = {}
    patch_edgedb_conversion_map: T.Dict[str, T.Dict[str, str]] = {}

    computed_properties: T.Set[str] = set()
    computed_property_getter_strs: T.List[str] = []

    appendix_properties: T.Set[str] = set()

    for prop in object_type.properties:
        conversion_type = edgedb_conversion_type_from_prop(prop)
        node_edgedb_conversion_map[prop.name] = {
            "cast": conversion_type,
            "cardinality": prop.cardinality.value,
            "readonly": prop.readonly,
        }
        if prop.is_computed:
            computed_properties.add(prop.name)
        is_appendix = False
        if node_config:
            if prop.name in node_config.appendix_properties:
                is_appendix = True
                appendix_properties.add(prop.name)
        if not prop.readonly and not prop.is_computed:
            updatable_fields.add(prop.name)
        if prop.is_exclusive:
            exclusive_fields.add(prop.name)
        default_value_str = "..." if prop.required else "None"
        allow_mutation_str = (
            f"allow_mutation={not prop.readonly and not prop.is_computed}"
        )
        if node_config and prop.name in node_config.basemodel_properties:
            prop_config = node_config.basemodel_properties[prop.name]
            module_name = prop_config.module_name
            type_str = prop.type_str_basemodel(
                module_name, cardinality=prop_config.cardinality
            )
        else:
            type_str = prop.type_str
        if not (prop.is_computed or is_appendix):
            property_strs.append(
                f"{prop.name}: {type_str} = Field({default_value_str}, {allow_mutation_str})"
            )
        else:
            if prop.is_computed:
                exception_name = "ComputedPropertyException"
                property_name = f"_{prop.name}"
                property_str = f"{property_name}: T.Union[{type_str}, Unset] = PrivateAttr(default_factory=Unset)"
            else:
                exception_name = "AppendixPropertyException"
                property_name = f"{prop.name}_"
                property_str = f'{property_name}: T.Union[{type_str}, Unset] = Field(default_factory=Unset, alias="{prop.name}")'
            property_strs.append(property_str)
            val_str = "val"
            if "Set[" in type_str:
                val_str = f"val if type(val) != list else set(val)"
            computed_property_getter_strs.append(
                f"""
@property
def {prop.name}(self) -> {type_str}:
    if is_unset(self.{property_name}):
        if "{prop.name}" in self.extra:
            val = self.extra["{prop.name}"]
            self.{property_name} = {val_str}
        else:
            raise {exception_name}("{prop.name} is unset")
    return self.{property_name}
                """
            )
            if not prop.is_computed:
                computed_property_getter_strs.append(
                    f"""
@{prop.name}.setter
def {prop.name}(self, {prop.name}: {type_str}) -> None:
    self.{property_name} = {prop.name}
                    """
                )
        if prop.name != "id":
            # for insert type
            if not prop.is_computed and not prop.not_insertable:
                insert_edgedb_conversion_map[prop.name] = {
                    "cast": conversion_type,
                    "cardinality": prop.cardinality.value,
                    "readonly": prop.readonly,
                }
                insert_type_str = type_str
                # if required but has default, add optional back
                if prop.required and prop.default:
                    insert_type_str = f"T.Optional[{insert_type_str}]"
                default_value_str = (
                    " = None" if insert_type_str.startswith("T.Optional[") else ""
                )
                insert_property_strs.append(
                    f"{prop.name}: {insert_type_str}{default_value_str}"
                )
            # for update type
            if not prop.is_computed and not prop.readonly:
                patch_edgedb_conversion_map[prop.name] = {
                    "cast": conversion_type,
                    "cardinality": prop.cardinality.value,
                    "readonly": prop.readonly,
                }
                patch_type_str = type_str
                if prop.required and prop.default:
                    patch_type_str = f"T.Optional[{patch_type_str}]"
                final_patch_type_str = f"T.Union[{patch_type_str}, Unset]"
                patch_property_strs.append(
                    f"{prop.name}: {final_patch_type_str} = Field(default_factory=Unset)"
                )

    link_function_strs: T.List[str] = []
    resolver_function_strs: T.List[str] = []
    updatable_links: T.Set[str] = set()
    exclusive_links: T.Set[str] = set()
    link_conversion_map: T.Dict[str, T.Dict[str, str]] = {}
    edge_resolver_map: T.Dict[str, str] = {}

    for link in object_type.links:
        if link.name == "__type__":
            continue
        link_conversion_map[link.name] = {
            "cast": link.target.model_name,
            "cardinality": link.cardinality.value,
            "readonly": link.readonly,
            "required": link.required,
        }
        edge_resolver_map[link.name] = f"{link.target.model_name}Resolver"
        if not link.readonly and not link.is_computed:
            updatable_links.add(link.name)
        if link.is_exclusive:
            exclusive_links.add(link.name)
        link_function_strs.append(build_node_link_function_str(link))
        resolver_function_strs.append(
            build_resolver_link_function_str(
                node_resolver_name=node_resolver_name, link=link
            )
        )
        # for insert
        if not link.is_computed and not link.not_insertable:
            insert_resolver_str = f"{link.target.model_name}Resolver"
            if (not link.required) or (link.required and link.default):
                insert_resolver_str = f"T.Optional[{insert_resolver_str}]"
            default_value_str = (
                " = None" if insert_resolver_str.startswith("T.Optional[") else ""
            )
            insert_property_strs.append(
                f"{link.name}: {insert_resolver_str}{default_value_str}"
            )
        # for update
        if not link.is_computed and not link.readonly:
            patch_resolver_str = f"{link.target.model_name}Resolver"
            if (not link.required) or (link.required and link.default):
                patch_resolver_str = f"T.Optional[{patch_resolver_str}]"
            final_patch_resolver_str = f"T.Union[{patch_resolver_str}, Unset]"
            patch_property_strs.append(
                f"{link.name}: {final_patch_resolver_str} = Field(default_factory=Unset)"
            )

    orm_config_str = build_orm_config(
        model_name=object_type.node_name,
        updatable_fields={*updatable_fields, *updatable_links},
        exclusive_fields={*exclusive_fields, *exclusive_links},
    )

    insert_model_name = f"{object_type.node_name}Insert"
    patch_model_name = f"{object_type.node_name}Patch"

    # insert type
    insert_inner_str = "\n".join(insert_property_strs)
    insert_conversion_map_str = f"_edgedb_conversion_map: T.ClassVar[T.Dict[str, str]] = {stringify_dict(insert_edgedb_conversion_map)}"
    insert_s = f"class {insert_model_name}(BaseModel):\n{indent_lines(insert_inner_str)}\n\n{indent_lines(insert_conversion_map_str)}"

    # patch type
    patch_inner_str = "\n".join(patch_property_strs)
    patch_conversion_map_str = f"_edgedb_conversion_map: T.ClassVar[T.Dict[str, str]] = {stringify_dict(patch_edgedb_conversion_map)}"
    patch_s = f"class {patch_model_name}(BasePatch):\n{indent_lines(patch_inner_str)}\n\n{indent_lines(patch_conversion_map_str)}"

    # node
    node_properties_str = "\n".join(property_strs)
    from_str_validator_str = build_from_str_validator_str(node_config=node_config)
    if hydrate:
        node_properties_str = ""
        from_str_validator_str = ""

    computed_property_getter_str = "\n".join(computed_property_getter_strs)
    node_conversion_map_str = f"_edgedb_conversion_map: T.ClassVar[T.Dict[str, str]] = {stringify_dict(node_edgedb_conversion_map)}"
    insert_link_conversion_map_str = f"_link_conversion_map: T.ClassVar[T.Dict[str, str]] = {stringify_dict(link_conversion_map)}"
    computed_properties_str = f"_computed_properties: T.ClassVar[T.Set[str]] = {stringify_set(computed_properties)}"
    appendix_properties_str = f"_appendix_properties: T.ClassVar[T.Set[str]] = {stringify_set(appendix_properties)}"
    basemodel_properties = (
        [] if not node_config else node_config.basemodel_properties.keys()
    )
    basemodel_properties_str = f"_basemodel_properties: T.ClassVar[T.Set[str]] = {stringify_set(set(basemodel_properties))}"
    node_link_functions_str = "\n".join(link_function_strs)
    update_function_str = build_update_function_str(
        node_resolver_name=node_resolver_name, links=object_type.links
    )
    if dehydrate:
        node_link_functions_str = ""
        update_function_str = ""
    node_inner_strs = [
        node_properties_str,
        "\n",
        from_str_validator_str,
        "\n",
        computed_property_getter_str,
        node_conversion_map_str,
        insert_link_conversion_map_str,
        computed_properties_str,
        appendix_properties_str,
        basemodel_properties_str,
        node_link_functions_str,
        update_function_str,
        orm_config_str,
    ]
    node_inner_str = "\n".join(remove_falsies(node_inner_strs))
    node_outer_strs = []
    node_outer_str = "\n".join(remove_falsies(node_outer_strs))
    inherits = (
        f"Node[{insert_model_name}, {patch_model_name}]"
        if not hydrate
        else f"{object_type.node_name}Hydrated"
    )
    node_s = f"{node_outer_str}\nclass {object_type.node_name}({inherits}):\n{indent_lines(node_inner_str)}"

    # resolver
    resolver_properties_str = f"_node = {object_type.node_name}"
    resolver_link_functions_str = "\n".join(resolver_function_strs)
    resolver_get_functions_str = build_get_functions_str(
        node_name=object_type.node_name, exclusive_field_names=exclusive_fields
    )
    resolver_filter_functions_str = build_filter_functions_str(
        node_name=object_type.node_name, conversion_map=node_edgedb_conversion_map
    )

    edge_resolver_val_strs = [
        f"T.Type[{v}]" for v in sorted(set(edge_resolver_map.values()))
    ]
    union_type = (
        f"T.Union[{', '.join(edge_resolver_val_strs)}]"
        if edge_resolver_map
        else "EdgeResolverType"
    )
    edge_resolver_map_strs.append(
        f"{node_resolver_name}._edge_resolver_map: T.Dict[str, {union_type}] ="
        f" {stringify_dict(edge_resolver_map, stringify_value=False)}"
    )
    resolver_inner_strs = [
        resolver_properties_str,
        resolver_link_functions_str,
        resolver_get_functions_str,
        resolver_filter_functions_str,
    ]
    resolver_inner_str = "\n".join(resolver_inner_strs)
    resolver_s = f"class {node_resolver_name}(Resolver[{object_type.node_name}]):\n{indent_lines(resolver_inner_str)}"

    final_s = (
        f"{object_type.node_name}.{CONFIG_NAME}.resolver_type = {node_resolver_name}"
    )
    return f"{insert_s}\n{patch_s}\n{node_s}\n{resolver_s}\n{final_s}"


async def build_nodes_and_resolvers(
    client: edgedb.AsyncIOClient,
    db_config: DBConfig,
    nodes_to_hydrate: T.Set[str],
    dehydrate: bool,
) -> str:
    object_types = await introspect_objects(client)
    node_strs: T.List[str] = []
    edge_resolver_map_strs: T.List[str] = []
    for object_type in object_types:
        node_strs.append(
            build_node_and_resolver(
                object_type,
                node_config=db_config.nodes.get(object_type.node_name),
                edge_resolver_map_strs=edge_resolver_map_strs,
                hydrate=object_type.node_name in nodes_to_hydrate and not dehydrate,
                dehydrate=dehydrate,
            )
        )
    update_forward_refs_inserts_str = "\n".join(
        [f"{o.node_name}Insert.update_forward_refs()" for o in object_types]
    )
    update_forward_refs_nodes_str = "\n".join(
        [f"{o.node_name}.update_forward_refs()" for o in object_types]
    )
    nodes_str = "\n".join(node_strs)
    edge_resolver_map_str = "\n".join(edge_resolver_map_strs)
    return f"{nodes_str}\n\n{update_forward_refs_inserts_str}\n\n{update_forward_refs_nodes_str}\n\n{edge_resolver_map_str}"


def build_client(db_config: DBConfig) -> str:
    return f"""
client = create_async_client(
    tls_security="{db_config.tls_security.value}",
    host="{db_config.host}",
    password="{db_config.password}", 
    port={db_config.port}
)
    """


def validate_output_path(path: Path) -> None:
    if not os.path.isdir(path):
        if os.path.isfile(path):
            raise GeneratorException(
                f"output path {path=} must be a directory, not a file."
            )
        if not os.path.exists(path):
            os.makedirs(path)


def build_hydrate_imports(db_config: DBConfig) -> str:
    import_strs: T.List[str] = []
    for node_name, config in db_config.nodes.items():
        if config.module_path:
            hydrated_name = f"{node_name}Hydrated"
            import_strs.append(
                f"from {config.module_path} import {node_name} as {hydrated_name}"
            )
            # idk why i have the part below, was just copying from dgraph_orm, seems unecessary and wrong
            # import_strs.append(
            #     f"{hydrated_name}.{CONFIG_NAME}.resolver._node = {hydrated_name}"
            # )
    return "\n".join(import_strs)


def get_nodes_to_hydrate(db_config: DBConfig) -> T.Set[str]:
    node_names: T.Set[str] = set()
    for node_name, config in db_config.nodes.items():
        if config.module_path:
            node_names.add(node_name)
    return node_names


async def build_enums_from_config(db_config: DBConfig, include_strawberry: bool) -> str:
    client = edgedb.create_async_client(
        tls_security=db_config.tls_security,
        host=db_config.host,
        password=db_config.password,
        port=db_config.port,
    )
    enums_imports = build_enum_imports()
    enums_str = await build_enums(client, include_strawberry=include_strawberry)
    s = "\n".join([enums_imports, enums_str])
    s = format_str(s, mode=FileMode())
    return s


async def build_from_config(
    db_config: DBConfig,
    enums_module: str,
    hydrate: bool = False,
    dehydrate: bool = False,
) -> str:
    client = edgedb.create_async_client(
        tls_security=db_config.tls_security,
        host=db_config.host,
        password=db_config.password,
        port=db_config.port,
    )
    imports_str = imports(enums_module=enums_module)
    client_str = build_client(db_config)
    validator_module_imports = build_validator_module_imports(db_config)
    hydrate_imports = "" if not hydrate else build_hydrate_imports(db_config)
    nodes_and_resolvers_str = await build_nodes_and_resolvers(
        client,
        db_config=db_config,
        nodes_to_hydrate=get_nodes_to_hydrate(db_config),
        dehydrate=dehydrate,
    )

    s = "\n".join(
        [
            imports_str,
            client_str,
            validator_module_imports,
            hydrate_imports,
            nodes_and_resolvers_str,
        ]
    )
    s = format_str(s, mode=FileMode())
    return s


async def generate(
    config_path: Path, output_path: Path, include_strawberry: bool = False
) -> None:
    validate_output_path(output_path)
    all_config_json_str = open(config_path).read()
    all_config_d = parse_raw_as(T.Dict[str, DBConfig], all_config_json_str)
    for db_name, db_config in all_config_d.items():
        if db_config.copy_config:
            db_config_to_copy = all_config_d[db_config.copy_config]
            db_config.hydrate = db_config_to_copy.hydrate
            db_config.nodes = db_config_to_copy.nodes

        # first build enums folder
        enums_s = await build_enums_from_config(
            db_config=db_config, include_strawberry=include_strawberry
        )
        enums_module = f"{db_name}_enums"
        open(output_path / f"{enums_module}.py", "w").write(enums_s)
        hydrate = db_config.hydrate
        # must include strawberry types in both for circular dependency reasons
        s = await build_from_config(
            db_config=db_config,
            dehydrate=hydrate,
            enums_module=enums_module,
        )
        open(output_path / f"{db_name}.py", "w").write(s)
        if hydrate:
            s = await build_from_config(
                db_config=db_config,
                hydrate=True,
                enums_module=enums_module,
            )
            open(output_path / f"{db_name}_hydrated.py", "w").write(s)
