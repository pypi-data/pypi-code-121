from __future__ import annotations

from typing import TYPE_CHECKING
from typing import List as TypingList
from typing import Optional, TypeVar

from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


PythonElementType = TypeVar("PythonElementType")
ProtobufElementType = TypeVar("ProtobufElementType")


class List(DataType[TypingList[ProtobufElementType], TypingList[PythonElementType]]):
    def __init__(self, fdl_node, parent_feature: Feature, parent_namespace):
        self.element_type: DataType[ProtobufElementType, PythonElementType] = DataType.from_fdl_node(
            xpath_sila(fdl_node, "sila:DataType")[0], parent_feature, parent_namespace
        )

    def to_native_type(
        self, message: TypingList[ProtobufElementType], toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> TypingList[PythonElementType]:
        return [
            self.element_type.to_native_type(item, toplevel_named_data_node=toplevel_named_data_node)
            for item in message
        ]

    def to_message(
        self, items: TypingList[PythonElementType], toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> TypingList[ProtobufElementType]:
        return [self.element_type.to_message(item, toplevel_named_data_node=toplevel_named_data_node) for item in items]
