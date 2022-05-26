from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from google.protobuf.message import Message

from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.fully_qualified_identifier import FullyQualifiedDataTypeIdentifier
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


class DataTypeDefinition(NamedDataNode, DataType):
    parent_feature: Feature
    fully_qualified_identifier: FullyQualifiedDataTypeIdentifier
    data_type: DataType

    def __init__(self, fdl_node, parent_feature: Feature):
        self.message_type = getattr(
            parent_feature._pb2_module,
            f"DataType_{xpath_sila(fdl_node, 'sila:Identifier/text()')[0]}",
        )
        super().__init__(fdl_node, parent_feature, self.message_type)
        self.parent_feature = parent_feature
        self.fully_qualified_identifier = FullyQualifiedDataTypeIdentifier(
            f"{parent_feature.fully_qualified_identifier}/DataType/{self._identifier}"
        )

    def to_native_type(self, message: Message, toplevel_named_data_node: Optional[NamedDataNode] = None) -> Any:
        return self.data_type.to_native_type(
            getattr(message, self._identifier), toplevel_named_data_node=toplevel_named_data_node
        )

    def to_message(self, *args: Any, **kwargs: Any) -> Message:
        return self.message_type(**{self._identifier: self.data_type.to_message(*args, **kwargs)})
