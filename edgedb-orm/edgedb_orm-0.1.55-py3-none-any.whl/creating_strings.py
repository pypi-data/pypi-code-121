import typing as T
from devtools import debug
from pydantic import BaseModel

if T.TYPE_CHECKING:
    from .node import Node

    NodeType = T.TypeVar("NodeType", bound=Node)
    InsertType = T.TypeVar("InsertType", bound=BaseModel)


def mutation_strs_from_fields(
    field_names: T.List[str],
    conversion_map: T.Dict[str, T.Dict[str, str]],
    from_json: bool,
) -> T.List[str]:
    """[slug := <str>json_get(item, 'slug'), tags := <array<str>>json_get(item, 'tags')]"""
    field_strs: T.List[str] = []
    for field_name in field_names:
        if conversion_info := conversion_map.get(field_name):
            cast = f"<{conversion_info['cast']}>"
            if conversion_info["cardinality"] == "Many":
                cast = f"<array{cast}>"
            if from_json:
                value = f"{cast}json_get(item, '{field_name}')"
            else:
                value = f"{cast}${field_name}"
            if conversion_info["cardinality"] == "Many":
                value = f"array_unpack({value})"
            field_strs.append(f"{field_name} := {value}")
    return field_strs


def insert_str_from_cls(
    insert_cls: T.Type["InsertType"],
    node_cls: T.Type["NodeType"],
    edge_filter_strs: T.List[str],
    upsert_given_conflict_on: str = None,
    return_conflicting_model_on: str = None,
    custom_on_conflict_str: str = None,
    from_json: bool = True,
) -> str:
    """insert Person { first_name := <str>$first_name } OR insert Person { first_name := <str>item['first_name'] }"""
    insertable_fields = insert_cls.__fields__.keys()
    conversion_map = insert_cls._edgedb_conversion_map
    insertable_field_strs = mutation_strs_from_fields(
        field_names=insertable_fields,
        conversion_map=conversion_map,
        from_json=from_json,
    )
    insertable_field_strs.extend(edge_filter_strs)
    inner_insert_str = ", ".join(insertable_field_strs)
    # put this in a with block because of https://github.com/edgedb/edgedb/issues/3675
    edge_field_names = [s.strip().split(" ")[0] for s in edge_filter_strs]
    insertable_non_link_fields = set(insertable_fields) - set(
        node_cls._link_conversion_map.keys()
    )
    variable_fields = ", ".join(
        [f"{f} := {f}" for f in [*insertable_non_link_fields, *edge_field_names]]
    )
    # need to add edges to variable fields
    insert_str = (
        f"WITH {inner_insert_str} INSERT {node_cls._model_name} {{{variable_fields}}}"
    )
    conflict_str = ""
    if custom_on_conflict_str:
        conflict_str = custom_on_conflict_str
    elif upsert_given_conflict_on:
        fields_to_update = node_cls.GraphORM.updatable_fields & set(
            conversion_map.keys()
        )
        update_variable_fields = ", ".join(
            [f"{f} := {f}" for f in [*fields_to_update, *edge_field_names]]
        )
        conflict_str = (
            f"UNLESS CONFLICT ON .{upsert_given_conflict_on} ELSE "
            f"(UPDATE {node_cls._model_name} SET {{{update_variable_fields}}})"
        )
    elif return_conflicting_model_on:
        conflict_str = f"UNLESS CONFLICT ON .{return_conflicting_model_on} ELSE (SELECT {node_cls._model_name})"
        # conflict_str = f"UNLESS CONFLICT on .slug ELSE (SELECT {node_cls._model_name})"
    if conflict_str:
        insert_str += f" {conflict_str}"
    return insert_str


def update_str_from_cls() -> str:
    ...
