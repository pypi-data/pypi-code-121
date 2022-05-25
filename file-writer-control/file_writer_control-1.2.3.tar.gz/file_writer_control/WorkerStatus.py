from datetime import datetime, timedelta
from enum import Enum, auto

STATUS_MESSAGE_TIMEOUT = timedelta(seconds=5)


class WorkerState(Enum):
    """
    The state of a worker (i.e. a file-writer instance).
    """

    IDLE = auto()
    WRITING = auto()
    UNKNOWN = auto()
    UNAVAILABLE = auto()


class WorkerStatus(object):
    """
    Contains general status information about a worker.
    """

    def __init__(self, service_id: str):
        self._last_update = datetime.now()
        self._service_id = service_id
        self._state = WorkerState.UNAVAILABLE

    def __eq__(self, other_status: "WorkerStatus") -> bool:
        if not isinstance(other_status, WorkerStatus):
            raise NotImplementedError
        return (
            self.service_id == other_status.service_id
            and self.state == other_status.state
        )

    def update_status(self, new_status: "WorkerStatus"):
        """
        Updates the status/state of this instance of the WorkerStatus class using another instance.
        .. note:: The service identifier of both this instance and the other one must be identical.
        :param new_status: The other instance of the WorkerStatus class.
        """
        if new_status.service_id != self.service_id:
            raise RuntimeError(
                f"Service id of status update is not correct ({self.service_id} vs {new_status.service_id})"
            )
        self._state = new_status.state
        self._last_update = new_status.last_update

    def check_if_outdated(self, current_time: datetime):
        """
        Given the current time, state and the time of the last update: Have we lost the connection?
        :param current_time: The current time
        """
        if (
            self.state != WorkerState.UNAVAILABLE
            and current_time - self.last_update > STATUS_MESSAGE_TIMEOUT
        ):
            self._state = WorkerState.UNAVAILABLE
            self._last_update = current_time

    @property
    def state(self) -> WorkerState:
        """
        The current state of the worker.
        """
        return self._state

    @property
    def service_id(self) -> str:
        """
        The service identifier of the worker that this instance of the WorkerState class represent.
        """
        return self._service_id

    @property
    def last_update(self) -> datetime:
        """
        The local time stamp of the last update of the status of the file-writer instance that this instance of the
        WorkerStatus class represents.
        """
        return self._last_update

    @state.setter
    def state(self, new_state: WorkerState):
        self._last_update = datetime.now()
        self._state = new_state
