from __future__ import annotations

from datetime import timedelta
from typing import Optional, Tuple, Type
from uuid import UUID

from sila2.framework.abc.message_mappable import MessageMappable
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.command.command_execution_uuid import CommandExecutionUUID
from sila2.framework.command.duration import Duration
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import CommandConfirmation as SilaCommandConfirmation


class CommandConfirmation(MessageMappable):
    native_type = Tuple[UUID, Optional[timedelta]]
    message_type: Type[SilaCommandConfirmation]

    def __init__(self, silaframework_pb2_module: SiLAFramework_pb2):
        self.message_type = silaframework_pb2_module.CommandConfirmation
        self.__duration_field = Duration(silaframework_pb2_module)
        self.__exec_id_field = CommandExecutionUUID(silaframework_pb2_module)

    def to_native_type(
        self, message: SilaCommandConfirmation, toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> Tuple[UUID, Optional[timedelta]]:
        exec_id = self.__exec_id_field.to_native_type(message.commandExecutionUUID)
        if message.HasField("lifetimeOfExecution"):
            return exec_id, self.__duration_field.to_native_type(message.lifetimeOfExecution)
        else:
            return exec_id, None

    def to_message(
        self,
        execution_uuid: UUID,
        duration: Optional[timedelta] = None,
        toplevel_named_data_node: Optional[NamedDataNode] = None,
    ) -> SilaCommandConfirmation:
        exec_id = self.__exec_id_field.to_message(execution_uuid)
        if duration is None:
            return self.message_type(commandExecutionUUID=exec_id)
        return self.message_type(
            commandExecutionUUID=exec_id,
            lifetimeOfExecution=self.__duration_field.to_message(duration),
        )
