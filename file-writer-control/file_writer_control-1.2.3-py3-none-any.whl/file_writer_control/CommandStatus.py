from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Optional

COMMAND_STATUS_TIMEOUT = timedelta(seconds=60)


class CommandState(Enum):
    """
    The state of a command.
    """

    UNKNOWN = auto()
    NO_COMMAND = auto()
    WAITING_RESPONSE = auto()
    TIMEOUT_RESPONSE = auto()
    ERROR = auto()
    SUCCESS = auto()


class CommandStatus(object):
    """
    The status of a command.
    """

    def __init__(
        self,
        job_id: str,
        command_id: str,
        command_timeout: timedelta = COMMAND_STATUS_TIMEOUT,
    ):
        self._command_timeout = command_timeout
        self._job_id = job_id
        self._command_id = command_id
        self._last_update = datetime.now()
        self._state = CommandState.NO_COMMAND
        self._message = ""
        self._response_code = None

    def __eq__(self, other_status: "CommandStatus"):
        if not isinstance(other_status, CommandStatus):
            raise NotImplementedError
        return (
            other_status.command_id == self.command_id
            and other_status.job_id == self.job_id
            and other_status.state == self.state
            and other_status.response_code == self.response_code
        )

    def update_status(self, new_status: "CommandStatus"):
        """
        Updates the status/state of this instance of the CommandStatus class using another instance.
        .. note:: The command identifier of both this instance and the other one must be identical.
        :param new_status: The other instance of the CommandStatus class.
        """
        if new_status.command_id != self.command_id:
            raise RuntimeError(
                f"Command id of status update is not correct ({self.command_id} vs {new_status.command_id})"
            )
        self._state = new_status.state
        self._response_code = new_status.response_code
        if new_status.message:
            self._message = new_status.message
        self._last_update = new_status.last_update

    def check_if_outdated(self, current_time: datetime):
        """
        Given the current time, state and the time of the last update: Have we lost the connection?
        :param current_time: The current time
        """
        if (
            self.state != CommandState.SUCCESS
            and self.state != CommandState.ERROR
            and self.state != CommandState.TIMEOUT_RESPONSE
            and current_time - self.last_update > self._command_timeout
        ):
            self._state = CommandState.TIMEOUT_RESPONSE
            self._last_update = current_time

    @property
    def response_code(self) -> Optional[int]:
        """
        A code that mirrors the result of a command if a response has been received. Is set to None otherwise.
        """
        return self._response_code

    @response_code.setter
    def response_code(self, new_code: int):
        """
        Set the current response code.
        """
        self._response_code = new_code
        self._last_update = datetime.now()

    @property
    def job_id(self) -> str:
        """
        The job identifier under which this command is executed.
        """
        return self._job_id

    @property
    def command_id(self) -> str:
        """
        The unique command identifier of this command.
        """
        return self._command_id

    @property
    def message(self) -> str:
        """
        A status/error message as returned by the file-writer that responded to the command.
        :return:
        """
        return self._message

    @message.setter
    def message(self, new_message: str):
        if new_message:
            self._message = new_message
            self._last_update = datetime.now()

    @property
    def state(self) -> CommandState:
        """
        The current state of the command.
        """
        return self._state

    @state.setter
    def state(self, new_state: CommandState):
        self._state = new_state
        self._last_update = datetime.now()

    @property
    def last_update(self) -> datetime:
        """
        The local time stamp of the last update of the status of the command.
        """
        return self._last_update

    @property
    def timeout(self) -> timedelta:
        """
        Timeout for waiting for response to command.
        """
        return self._command_timeout

    @timeout.setter
    def timeout(self, new_timeout: timedelta):
        self._command_timeout = new_timeout
