from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Optional, Type

from sila2.framework.abc.message_mappable import MessageMappable
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.command.duration import Duration
from sila2.framework.data_types.real import Real
from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import ExecutionInfo as SilaExecutionInfo


class ExecutionInfo(MessageMappable):
    message_type: Type[SilaExecutionInfo]

    def __init__(self, silaframework_pb2_module: SiLAFramework_pb2):
        self.message_type = silaframework_pb2_module.ExecutionInfo
        self.__real_field = Real(silaframework_pb2_module)
        self.__duration_field = Duration(silaframework_pb2_module)

    def to_native_type(
        self, message: SilaExecutionInfo, toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> CommandExecutionInfo:
        status = getattr(CommandExecutionStatus, self.message_type.CommandStatus.Name(message.commandStatus))
        progress, estimated_remaining_time, updated_lifetime_of_execution = (
            None,
            None,
            None,
        )

        if message.HasField("progressInfo"):
            progress = self.__real_field.to_native_type(message.progressInfo)

        if message.HasField("estimatedRemainingTime"):
            estimated_remaining_time = self.__duration_field.to_native_type(message.estimatedRemainingTime)

        if message.HasField("updatedLifetimeOfExecution"):
            updated_lifetime_of_execution = self.__duration_field.to_native_type(message.updatedLifetimeOfExecution)

        return CommandExecutionInfo(
            status=status,
            progress=progress,
            estimated_remaining_time=estimated_remaining_time,
            updated_lifetime_of_execution=updated_lifetime_of_execution,
        )

    def to_message(
        self, value: CommandExecutionInfo, toplevel_named_data_node: Optional[NamedDataNode] = None
    ) -> SilaExecutionInfo:
        progress = None if value.progress is None else self.__real_field.to_message(value.progress)
        estimated_remaining_time = (
            None
            if value.estimated_remaining_time is None
            else self.__duration_field.to_message(value.estimated_remaining_time)
        )
        updated_lifetime_of_execution = (
            None
            if value.updated_lifetime_of_execution is None
            else self.__duration_field.to_message(value.updated_lifetime_of_execution)
        )

        return self.message_type(
            commandStatus=value.status.value,
            progressInfo=progress,
            estimatedRemainingTime=estimated_remaining_time,
            updatedLifetimeOfExecution=updated_lifetime_of_execution,
        )


@dataclass
class CommandExecutionInfo:
    status: CommandExecutionStatus
    progress: Optional[float] = None
    estimated_remaining_time: Optional[timedelta] = None
    updated_lifetime_of_execution: Optional[timedelta] = None


class CommandExecutionStatus(Enum):
    """Status of an observable command instance"""

    waiting = 0
    running = 1
    finishedSuccessfully = 2
    finishedWithError = 3
