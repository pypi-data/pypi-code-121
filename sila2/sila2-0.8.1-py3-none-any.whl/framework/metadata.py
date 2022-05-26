from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, List, Optional, Type, TypeVar, Union

from google.protobuf.message import Message

from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.command.command import Command
from sila2.framework.data_types.binary import Binary
from sila2.framework.data_types.string import String
from sila2.framework.fully_qualified_identifier import FullyQualifiedIdentifier, FullyQualifiedMetadataIdentifier
from sila2.framework.pb2.custom_protocols import AffectedCallsMessage
from sila2.framework.property.property import Property
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.feature import Feature

T = TypeVar("T")


class Metadata(NamedDataNode, Generic[T]):
    """Metadata defined in a SiLA feature"""

    fully_qualified_identifier: FullyQualifiedMetadataIdentifier
    """Fully qualified metadata identifier"""

    def __init__(self, fdl_node, parent_feature: Feature):
        identifier = xpath_sila(fdl_node, "sila:Identifier/text()")[0]
        super().__init__(fdl_node, parent_feature, getattr(parent_feature._pb2_module, f"Metadata_{identifier}"))
        self.parent_feature = parent_feature
        self.fully_qualified_identifier = FullyQualifiedMetadataIdentifier(
            f"{parent_feature.fully_qualified_identifier}/Metadata/{self._identifier}"
        )
        self.defined_execution_errors = [
            parent_feature.defined_execution_errors[name]
            for name in xpath_sila(fdl_node, "sila:DefinedExecutionErrors/sila:Identifier/text()")
        ]

        self.message_type: Type[Message] = getattr(self.parent_feature._pb2_module, f"Metadata_{self._identifier}")
        self.parameter_message_type: Type[Message] = getattr(
            self.parent_feature._pb2_module,
            f"Metadata_{self._identifier}",
        )
        self.affected_calls_responses_message_type: Type[AffectedCallsMessage] = getattr(
            self.parent_feature._pb2_module,
            f"Get_FCPAffectedByMetadata_{self._identifier}_Responses",
        )
        self.affected_calls_parameters_message_type: Type[Message] = getattr(
            self.parent_feature._pb2_module,
            f"Get_FCPAffectedByMetadata_{self._identifier}_Parameters",
        )
        self.__string_field = String(parent_feature._pb2_module.SiLAFramework__pb2)

    def get_parameter_message(self) -> Message:
        return self.parameter_message_type()

    def get_affected_calls_parameters_message(self) -> Message:
        return self.affected_calls_parameters_message_type()

    def to_affected_calls_message(
        self, affected_targets: List[Union[Feature, Property, Command, FullyQualifiedIdentifier]]
    ) -> AffectedCallsMessage:
        identifiers = []
        for target in affected_targets:
            if isinstance(target, str):
                identifiers.append(target)
            else:
                identifiers.append(target.fully_qualified_identifier)
        return self.affected_calls_responses_message_type(
            AffectedCalls=[self.__string_field.to_message(target) for target in identifiers]
        )

    def to_message(self, value: Any, toplevel_named_data_node: Optional[NamedDataNode] = None) -> bytes:
        return self.message_type(
            **{self._identifier: self.data_type.to_message(value, toplevel_named_data_node=toplevel_named_data_node)}
        ).SerializeToString()

    def to_native_type(self, msg: bytes) -> Any:
        pb2_msg = self.message_type.FromString(msg)
        if isinstance(self.data_type, Binary) and getattr(pb2_msg, self._identifier).HasField("binaryTransferUUID"):
            raise ValueError("Cannot use Binary Transfer for SiLA Client Metadata")
        return self.data_type.to_native_type(getattr(pb2_msg, self._identifier))

    def to_grpc_header_key(self) -> str:
        return f"sila-{self.fully_qualified_identifier.lower().replace('/', '-')}-bin"
