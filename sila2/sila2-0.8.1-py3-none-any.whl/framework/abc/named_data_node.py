from __future__ import annotations

from typing import TYPE_CHECKING, Generic

from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.message_mappable import ProtobufType, PythonType
from sila2.framework.abc.named_node import NamedNode
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


class NamedDataNode(NamedNode, Generic[ProtobufType, PythonType]):
    data_type: DataType[ProtobufType, PythonType]

    def __init__(self, fdl_node, parent_feature: Feature, parent_namespace):
        super().__init__(fdl_node)
        self.data_type = DataType.from_fdl_node(
            xpath_sila(fdl_node, "sila:DataType")[0], parent_feature, parent_namespace
        )
