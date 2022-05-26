from __future__ import annotations

from typing import TYPE_CHECKING, Union

from sila2.framework.abc.constraint import Constraint

if TYPE_CHECKING:
    from sila2.framework.abc.data_type import DataType
    from sila2.framework.feature import Feature


class MaximalLength(Constraint):
    max_length: int

    def __init__(self, max_length: int):
        if max_length < 0:
            raise ValueError("Length cannot be negative")
        if max_length > 2**63 - 1:
            raise ValueError("Length cannot be greater than 2^63 - 1")
        self.max_length = max_length

    def validate(self, value: Union[str, bytes]) -> bool:
        return len(value) <= self.max_length

    @classmethod
    def from_fdl_node(cls, fdl_node, parent_feature: Feature, base_type: DataType) -> MaximalLength:
        return cls(int(fdl_node.text))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.max_length})"
