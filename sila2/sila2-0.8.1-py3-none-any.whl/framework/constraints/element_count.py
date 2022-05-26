from __future__ import annotations

from typing import TYPE_CHECKING

from sila2.framework.abc.constraint import Constraint

if TYPE_CHECKING:
    from sila2.framework.abc.data_type import DataType
    from sila2.framework.feature import Feature


class ElementCount(Constraint[list]):
    element_count: int

    def __init__(self, element_count: int):
        self.element_count = element_count

    def validate(self, value: list) -> bool:
        return len(value) == self.element_count

    @classmethod
    def from_fdl_node(cls, fdl_node, parent_feature: Feature, base_type: DataType) -> ElementCount:
        return cls(int(fdl_node.text))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.element_count})"
