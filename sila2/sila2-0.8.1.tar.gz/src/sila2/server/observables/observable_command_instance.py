from __future__ import annotations

from datetime import timedelta
from queue import Queue
from typing import Generic, Optional, TypeVar

from sila2.framework import CommandExecutionInfo, CommandExecutionStatus


class ObservableCommandInstance:
    """Instance of a currently running observable command. Provides means to update the execution information."""

    def __init__(self, execution_info_queue: Queue[CommandExecutionInfo]):
        self.__progress: Optional[float] = None
        self.__estimated_remaining_time: Optional[timedelta] = None
        self.__status: CommandExecutionStatus = CommandExecutionStatus.running
        self.__info_queue: Queue[CommandExecutionInfo] = execution_info_queue

    @property
    def status(self) -> CommandExecutionStatus:
        """
        Command execution status. Clients are notified about updates.
        """
        return self.__status

    @status.setter
    def status(self, status: CommandExecutionStatus) -> None:
        if not isinstance(status, CommandExecutionStatus):
            raise TypeError(f"Expected a {CommandExecutionStatus.__class__.__name__}, got {status}")
        self.__status = status
        self.__update_execution_info()

    @property
    def progress(self) -> Optional[float]:
        """Command execution progress. Must be ``None``, or between 0 and 100. Clients are notified about updates."""
        return self.__progress

    @progress.setter
    def progress(self, progress: float) -> None:
        if not isinstance(progress, (int, float)):
            raise TypeError(f"Expected an int or float, got {progress}")
        if progress < 0 or progress > 100:
            raise ValueError("Progress must be between 0 and 100")
        self.__progress = progress
        self.__update_execution_info()

    @property
    def estimated_remaining_time(self) -> Optional[timedelta]:
        """Command execution progress. Must be ``None``, or a positive timedelta. Clients are notified about updates."""
        return self.__estimated_remaining_time

    @estimated_remaining_time.setter
    def estimated_remaining_time(self, estimated_remaining_time: timedelta) -> None:
        if not isinstance(estimated_remaining_time, timedelta):
            raise TypeError(f"Expected a datetime.timedelta, got {estimated_remaining_time}")
        if estimated_remaining_time.total_seconds() < 0:
            raise ValueError("Estimated remaining time cannot be negative")
        self.__estimated_remaining_time = estimated_remaining_time
        self.__update_execution_info()

    def __update_execution_info(self) -> None:
        if self.__status is None:
            self.__status = CommandExecutionStatus.running

        self.__info_queue.put(CommandExecutionInfo(self.__status, self.__progress, self.__estimated_remaining_time))


IntermediateResponseType = TypeVar("IntermediateResponseType")


class ObservableCommandInstanceWithIntermediateResponses(ObservableCommandInstance, Generic[IntermediateResponseType]):
    """
    Instance of a currently running observable command.
    Provides means to update the execution information and send intermediate responses.
    """

    def __init__(
        self,
        execution_info_queue: Queue[CommandExecutionInfo],
        intermediate_response_queue: Queue[IntermediateResponseType],
    ):
        super().__init__(execution_info_queue)
        self.__intermediate_response_queue: Queue[IntermediateResponseType] = intermediate_response_queue

    def send_intermediate_response(self, value: IntermediateResponseType) -> None:
        """
        Send intermediate responses to subscribing clients

        Parameters
        ----------
        value
            The intermediate responses to send
        """
        self.__intermediate_response_queue.put(value)
