from __future__ import annotations

from typing import TYPE_CHECKING

from sila2.framework.abc.constraint import Constraint

if TYPE_CHECKING:
    from sila2.framework.abc.data_type import DataType
    from sila2.framework.feature import Feature


class MinimalElementCount(Constraint[list]):
    min_elements: int

    def __init__(self, min_elements: int):
        self.min_elements = min_elements

    def validate(self, value: list) -> bool:
        return len(value) >= self.min_elements

    @classmethod
    def from_fdl_node(cls, fdl_node, parent_feature: Feature, base_type: DataType) -> MinimalElementCount:
        return cls(int(fdl_node.text))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.min_elements})"
