from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Union

from sila2.framework.abc.constraint import Constraint

if TYPE_CHECKING:
    from sila2.framework.abc.data_type import DataType
    from sila2.framework.feature import Feature


T = TypeVar("T", bound=Union[str, bytes])


class MinimalLength(Constraint):
    min_length: int

    def __init__(self, min_length: int):
        if min_length < 0:
            raise ValueError("Length cannot be negative")
        if min_length > 2**63 - 1:
            raise ValueError("Length cannot be greater than 2^63 - 1")
        self.min_length = min_length

    def validate(self, value: Union[str, bytes]) -> bool:
        return len(value) >= self.min_length

    @classmethod
    def from_fdl_node(cls, fdl_node, parent_feature: Feature, base_type: DataType) -> MinimalLength:
        return cls(int(fdl_node.text))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.min_length})"
