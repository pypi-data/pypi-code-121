import typing as T
from pydantic import BaseModel, parse_raw_as
from pydantic.fields import ModelField

ModelType = T.TypeVar("ModelType", bound=BaseModel)


def from_str(cls, v, field: ModelField) -> ModelType:
    if type(v) is str:
        res = parse_raw_as(field.outer_type_, v)
        return res
    return v


from enum import Enum

EnumType = T.TypeVar("EnumType", bound=Enum)


def transform_enum(
    original_value: T.Union[str, Enum],
    new_enum_type: T.Type[EnumType],
    ignore_null: bool = False,
) -> T.Optional[EnumType]:
    if ignore_null:
        if original_value is None:
            return None
    if isinstance(original_value, Enum):
        original_value = original_value.value
    new_value = (
        original_value.replace("/", "")
        .replace("-", "_")
        .replace("  ", " ")
        .replace(" ", "_")
    )
    return new_enum_type(new_value)


def enum_from_str(cls, v, field: ModelField) -> EnumType:
    if type(v) is str or not isinstance(v, field.type_):
        return transform_enum(original_value=v, new_enum_type=field.type_)
    return v
