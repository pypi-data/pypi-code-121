"""Type hints used throughout ``ts-ids-core``."""

from typing import AbstractSet, Any, Dict, Generic, Mapping, Optional, TypeVar, Union

Nullable = Optional
NullableString = Nullable[str]
NullableBoolean = Nullable[bool]
NullableNumber = Nullable[float]
#: `NullableInt` indicates "the value is likely an integer, but since Athena doesn't
#: distinguish between integers and floats, we'll specify the value as the
#: more-permissive `float` type."
NullableInt = NullableNumber

#: Copied from `pydantic.typing` because they are not import-able.
IntStr = Union[int, str]
AbstractSetIntStr = AbstractSet[IntStr]
DictStrAny = Dict[str, Any]
MappingIntStrAny = Mapping[IntStr, Any]

T = TypeVar("T")


class Required(Generic[T]):
    """A type hint indicating that a field in a Programmatic IDS class is required."""
