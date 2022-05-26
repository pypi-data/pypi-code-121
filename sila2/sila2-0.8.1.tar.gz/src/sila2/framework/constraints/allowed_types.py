from __future__ import annotations

from typing import TYPE_CHECKING, List

from sila2.framework.abc.constraint import Constraint
from sila2.framework.data_types.any import SilaAnyType
from sila2.framework.utils import xml_node_to_normalized_string, xpath_sila

if TYPE_CHECKING:
    from sila2.framework.abc.data_type import DataType
    from sila2.framework.feature import Feature


class AllowedTypes(Constraint[SilaAnyType]):
    allowed_types: List[str]

    def __init__(self, allowed_types: List[str]):
        self.allowed_types = allowed_types

    def validate(self, value: SilaAnyType) -> bool:
        _type_str = xml_node_to_normalized_string(value.type_xml, remove_namespace=True)
        return any(_type_str == s for s in self.allowed_types)

    @classmethod
    def from_fdl_node(cls, fdl_node, parent_feature: Feature, base_type: DataType) -> AllowedTypes:
        return cls(
            [
                xml_node_to_normalized_string(dtype_node, remove_namespace=True)
                for dtype_node in xpath_sila(fdl_node, "sila:DataType")
            ]
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.allowed_types!r})"
