from ._inner import (
    InnerJsonSchema,
)
from decimal import (
    Decimal,
)
from enum import (
    Enum,
)
from fa_purity import (
    FrozenDict,
    FrozenList,
    JsonObj,
    JsonValue,
    Result,
    ResultE,
)
from fa_purity.json.primitive import (
    PrimitiveTypes,
)
from fa_purity.json.transform import (
    to_raw,
)
from fa_singer_io.json_schema.core import (
    JsonSchema,
)
from jsonschema import (
    Draft4Validator,
    SchemaError,
)
from typing import (
    FrozenSet,
)


class SupportedType(Enum):
    array = "array"
    boolean = "boolean"
    integer = "integer"
    null = "null"
    number = "number"
    object = "object"
    string = "string"


_encode_type = {
    bool: SupportedType.boolean,
    int: SupportedType.integer,
    type(None): SupportedType.null,
    Decimal: SupportedType.number,
    float: SupportedType.number,
    str: SupportedType.string,
}


def from_json(raw: JsonObj) -> ResultE[JsonSchema]:
    raw_dict = to_raw(raw)  # type: ignore[misc]
    try:
        Draft4Validator.check_schema(raw_dict)  # type: ignore[misc]
        validator = Draft4Validator(raw_dict)  # type: ignore[misc]
        draft = InnerJsonSchema(raw, validator)
        return Result.success(JsonSchema(draft))
    except SchemaError as err:  # type: ignore[misc]
        return Result.failure(err)


def multi_type(types: FrozenSet[PrimitiveTypes]) -> ResultE[JsonSchema]:
    if len(types) == 0:
        return Result.failure(Exception("Must specify a type"))
    _types: FrozenList[JsonValue] = tuple(
        JsonValue(_encode_type[t].value) for t in types
    )
    raw = {"type": JsonValue(_types) if len(_types) > 1 else _types[0]}
    return Result.success(from_json(FrozenDict(raw)).unwrap())


def from_prim_type(p_type: PrimitiveTypes) -> JsonSchema:
    raw = {"type": JsonValue(_encode_type[p_type].value)}
    return from_json(FrozenDict(raw)).unwrap()


def opt_prim_type(p_type: PrimitiveTypes) -> JsonSchema:
    return multi_type(frozenset([p_type, type(None)])).unwrap()


def datetime_schema() -> JsonSchema:
    json = {
        "type": JsonValue(_encode_type[str].value),
        "format": JsonValue("date-time"),
    }
    return from_json(FrozenDict(json)).unwrap()


def opt_datetime_schema() -> JsonSchema:
    base = opt_prim_type(str).encode()
    json = {
        "type": base["type"],
        "format": JsonValue("date-time"),
    }
    return from_json(FrozenDict(json)).unwrap()
