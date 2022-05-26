from __future__ import annotations

from threading import Thread
from typing import TYPE_CHECKING
from uuid import UUID

import grpc
from grpc import RpcError
from grpc._channel import _MultiThreadedRendezvous

from sila2.framework.command.execution_info import ExecutionInfo
from sila2.framework.fully_qualified_identifier import FullyQualifiedIdentifier

if TYPE_CHECKING:
    from sila2.client.client_observable_command_instance import ClientObservableCommandInstance


class ExecutionInfoSubscriptionThread(Thread):
    __stream: _MultiThreadedRendezvous
    __command_instance: ClientObservableCommandInstance
    __execution_info_field: ExecutionInfo

    def __init__(
        self,
        command_id: FullyQualifiedIdentifier,
        execution_uuid: UUID,
        stream: _MultiThreadedRendezvous,
        command_instance: ClientObservableCommandInstance,
    ):
        super().__init__(name=f"{self.__class__.__name__}-{command_id}-{execution_uuid}")
        self.__stream = stream
        self.__command_instance = command_instance
        self.__execution_info_field = ExecutionInfo(
            command_instance._client_command._wrapped_command.parent_feature._pb2_module.SiLAFramework__pb2
        )

    def run(self) -> None:
        try:
            for response_msg in self.__stream:
                execution_info = self.__execution_info_field.to_native_type(response_msg)
                self.__command_instance._update(execution_info)
        except RpcError as ex:
            if ex.code() == grpc.StatusCode.UNAVAILABLE:
                pass  # stream cancelled
            else:
                raise

    def cancel(self) -> None:
        self.__stream.cancel()
