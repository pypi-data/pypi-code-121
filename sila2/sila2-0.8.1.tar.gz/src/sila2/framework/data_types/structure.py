from __future__ import annotations

from sila2.framework.abc.composite_message_mappable import CompositeMessageMappable
from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.utils import xpath_sila


class StructureElement(NamedDataNode):
    data_type: DataType

    def __init__(self, fdl_node, parent_feature, parent_namespace):
        super().__init__(fdl_node, parent_feature, parent_namespace)


class Structure(CompositeMessageMappable[StructureElement], DataType):
    def __init__(self, fdl_node, parent_feature, parent_namespace):
        message_type = getattr(
            parent_namespace,
            xpath_sila(fdl_node, "ancestor::*/sila:Identifier/text()")[-1] + "_Struct",
        )
        super().__init__(
            [StructureElement(node, parent_feature, message_type) for node in xpath_sila(fdl_node, "sila:Element")],
            getattr(parent_namespace, xpath_sila(fdl_node, "ancestor::*/sila:Identifier/text()")[-1] + "_Struct"),
        )
