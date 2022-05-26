from __future__ import annotations

from typing import Optional, Type
from uuid import UUID

from sila2.framework.abc.message_mappable import MessageMappable
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import CommandExecutionUUID as SilaCommandExecutionUUID


class CommandExecutionUUID(MessageMappable):
    native_type = UUID
    message_type: Type[SilaCommandExecutionUUID]

    def __init__(self, silaframework_pb2_module: SiLAFramework_pb2):
        self.message_type = silaframework_pb2_module.CommandExecutionUUID

    def to_native_type(
        self, message: SilaCommandExecutionUUID, toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> UUID:
        return UUID(message.value)

    def to_message(
        self, value: UUID, toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> SilaCommandExecutionUUID:
        return self.message_type(value=str(value))
