from __future__ import annotations

from typing import TYPE_CHECKING

from sila2.framework.abc.constraint import Constraint

if TYPE_CHECKING:
    from sila2.framework.abc.data_type import DataType
    from sila2.framework.feature import Feature


class MaximalElementCount(Constraint[list]):
    max_elements: int

    def __init__(self, max_elements: int):
        self.max_elements = max_elements

    def validate(self, value: list) -> bool:
        return len(value) <= self.max_elements

    @classmethod
    def from_fdl_node(cls, fdl_node, parent_feature: Feature, base_type: DataType) -> MaximalElementCount:
        return cls(int(fdl_node.text))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.max_elements})"
