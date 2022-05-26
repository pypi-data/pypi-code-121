from __future__ import annotations

import datetime
import uuid
from concurrent.futures import Future
from queue import Queue
from typing import TYPE_CHECKING, Callable

from google.protobuf.message import Message

from sila2.framework.command.execution_info import CommandExecutionInfo, CommandExecutionStatus, ExecutionInfo
from sila2.framework.command.observable_command import ObservableCommand
from sila2.framework.errors.command_execution_not_finished import CommandExecutionNotFinished
from sila2.server.metadata_dict import MetadataDict
from sila2.server.observables.observable_command_instance import (
    ObservableCommandInstance,
    ObservableCommandInstanceWithIntermediateResponses,
)
from sila2.server.observables.stream import Stream
from sila2.server.observables.subscription_manager_thread import SubscriptionManagerThread

if TYPE_CHECKING:
    from grpc import ServicerContext

    from sila2.framework.pb2.SiLAFramework_pb2 import ExecutionInfo as SilaExecutionInfo
    from sila2.server.sila_server import SilaServer


class ObservableCommandManager:
    """Coordinates the execution of an observable command call"""

    def __init__(
        self,
        parent_server: SilaServer,
        wrapped_command: ObservableCommand,
        impl_func: Callable[[ObservableCommandInstance], Message],
        metadata: MetadataDict,
    ) -> None:
        self.parent_server = parent_server
        self.command_execution_uuid = uuid.uuid4()
        self.wrapped_command = wrapped_command
        self.metadata = metadata

        # prepare subscriptions
        self.execution_info_queue = Queue()
        self.intermediate_response_queue = Queue()
        self.info_subscription_thread = SubscriptionManagerThread(
            self.wrapped_command.fully_qualified_identifier,
            self.execution_info_queue,
            converter_func=ExecutionInfo(wrapped_command.parent_feature._pb2_module.SiLAFramework__pb2).to_message,
        )
        self.info_subscription_thread.start()

        if wrapped_command.intermediate_responses is not None:
            self.intermediate_response_subscription_thread = SubscriptionManagerThread(
                self.wrapped_command.fully_qualified_identifier,
                self.intermediate_response_queue,
                converter_func=wrapped_command.intermediate_responses.to_message,
            )
            self.intermediate_response_subscription_thread.start()
            command_instance = ObservableCommandInstanceWithIntermediateResponses(
                self.execution_info_queue, self.intermediate_response_queue
            )
        else:
            command_instance = ObservableCommandInstance(self.execution_info_queue)

        self.result_future = parent_server.child_task_executor.submit(impl_func, command_instance)
        self.result_future.add_done_callback(self.__after_execution)

    def subscribe_to_execution_infos(self, context: ServicerContext) -> Stream[SilaExecutionInfo]:
        if self.is_running():
            return self.info_subscription_thread.add_subscription(context)

        status = (
            CommandExecutionStatus.finishedSuccessfully
            if self.result_future.exception() is None
            else CommandExecutionStatus.finishedWithError
        )
        queue = Queue()
        queue.put(
            ExecutionInfo(self.wrapped_command.parent_feature._pb2_module.SiLAFramework__pb2).to_message(
                CommandExecutionInfo(status, 100, estimated_remaining_time=datetime.timedelta(0))
            )
        )
        stream = Stream.from_queue(queue)
        stream.cancel()
        return stream

    def subscribe_to_intermediate_responses(self, context: ServicerContext) -> Stream:
        stream = self.intermediate_response_subscription_thread.add_subscription(context)
        if not self.is_running():
            stream.cancel()  # else when subscribing after execution the stream will never end
        return stream

    def get_responses(self):
        if self.is_running():
            raise CommandExecutionNotFinished(
                f"Instance {self.command_execution_uuid} of command {self.wrapped_command._identifier} has not finished"
            )

        ex = self.result_future.exception()
        if ex is None:
            return self.result_future.result()
        raise ex

    def is_running(self) -> bool:
        return not self.result_future.done()

    def __after_execution(self, result_future: Future):
        ex = result_future.exception()
        status = CommandExecutionStatus.finishedSuccessfully if ex is None else CommandExecutionStatus.finishedWithError
        self.execution_info_queue.put(CommandExecutionInfo(status, 100, estimated_remaining_time=datetime.timedelta(0)))
        self.execution_info_queue.put(StopIteration())
        self.intermediate_response_queue.put(StopIteration())
