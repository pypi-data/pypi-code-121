from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Type

from google.protobuf.message import Message

from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.defined_execution_error_node import DefinedExecutionErrorNode
from sila2.framework.fully_qualified_identifier import FullyQualifiedPropertyIdentifier
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


class Property(NamedDataNode):
    """Represents a property"""

    fully_qualified_identifier: FullyQualifiedPropertyIdentifier
    """Fully qualified property identifier"""
    parent_feature: Feature
    parameter_message_type: Type[Message]
    response_message_type: Type[Message]
    defined_execution_errors: List[DefinedExecutionErrorNode]

    def __init__(self, fdl_node, parent_feature: Feature):
        identifier: str = xpath_sila(fdl_node, "sila:Identifier/text()")[0]
        observable = xpath_sila(fdl_node, "sila:Observable/text()")[0] == "Yes"
        message_prefix = "Subscribe_" if observable else "Get_"
        super().__init__(
            fdl_node, parent_feature, getattr(parent_feature._pb2_module, f"{message_prefix}{identifier}_Responses")
        )
        self.parent_feature = parent_feature
        self.fully_qualified_identifier = FullyQualifiedPropertyIdentifier(
            f"{parent_feature.fully_qualified_identifier}/Property/{self._identifier}"
        )
        self.defined_execution_errors = [
            parent_feature.defined_execution_errors[name]
            for name in xpath_sila(fdl_node, "sila:DefinedExecutionErrors/sila:Identifier/text()")
        ]

    @staticmethod
    def from_fdl_node(fdl_node, parent_feature: Feature) -> Property:
        if xpath_sila(fdl_node, "sila:Observable/text() = 'No'"):
            from sila2.framework.property.unobservable_property import UnobservableProperty

            return UnobservableProperty(fdl_node, parent_feature)

        from sila2.framework.property.observable_property import ObservableProperty

        return ObservableProperty(fdl_node, parent_feature)

    def get_parameters_message(self) -> Message:
        return self.parameter_message_type()

    def to_native_type(self, msg: Message, toplevel_named_data_node: Optional[NamedDataNode] = None) -> Any:
        return self.data_type.to_native_type(
            getattr(msg, self._identifier), toplevel_named_data_node=toplevel_named_data_node
        )

    def to_message(self, value: Any, toplevel_named_data_node: Optional[NamedDataNode] = None) -> Message:
        return self.response_message_type(
            **{self._identifier: self.data_type.to_message(value, toplevel_named_data_node=toplevel_named_data_node)}
        )
