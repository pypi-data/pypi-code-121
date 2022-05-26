from __future__ import annotations

import re
from typing import TYPE_CHECKING

from sila2.framework.abc.constraint import Constraint

if TYPE_CHECKING:
    from sila2.framework.abc.data_type import DataType
    from sila2.framework.feature import Feature


class Pattern(Constraint[str]):
    pattern: str

    def __init__(self, pattern: str):
        self.pattern = pattern

    def validate(self, value: str) -> bool:
        return bool(re.fullmatch(self.pattern, value))

    @classmethod
    def from_fdl_node(cls, fdl_node, parent_feature: Feature, base_type: DataType) -> Pattern:
        return cls(fdl_node.text)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.pattern!r})"
