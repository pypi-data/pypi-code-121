from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Optional, Dict

JOB_STATUS_TIMEOUT = timedelta(seconds=5)


class JobState(Enum):
    """
    The state of a job.
    """

    NO_JOB = auto()
    WAITING = auto()
    WRITING = auto()
    TIMEOUT = auto()
    ERROR = auto()
    DONE = auto()
    UNAVAILABLE = auto()


class JobStatus:
    """
    Contains general information about the (execution) of a job.
    """

    def __init__(self, job_id: str):
        self._job_id = job_id
        self._service_id = ""
        self._file_name = ""
        self._last_update = datetime.now()
        self._state = JobState.WAITING
        self._metadata: Optional[Dict] = None
        self._message = ""

    def update_status(self, new_status: "JobStatus") -> None:
        """
        Updates the status/state of a this instance of the JobStatus class, using another instance.
        .. note:: The job identifier of this instance and the other must be identical.
        :param new_status: The other instance of the JobStatus class.
        """
        if new_status.job_id != self.job_id:
            raise RuntimeError(
                f"Job id of status update is not correct ({self.job_id} vs {new_status.job_id})"
            )
        self._state = new_status.state
        if new_status.message:
            self._message = new_status.message
        self._service_id = new_status.service_id
        self._file_name = new_status.file_name
        self._last_update = new_status.last_update
        self._metadata = new_status.metadata

    def check_if_outdated(self, current_time: datetime):
        """
        Given the current time, state and the time of the last update: Have we lost the connection?
        :param current_time: The current time
        """
        if (
            self.state != JobState.DONE
            and self.state != JobState.ERROR
            and self.state != JobState.TIMEOUT
            and current_time - self.last_update > JOB_STATUS_TIMEOUT
        ):
            self._state = JobState.TIMEOUT
            self._last_update = current_time

    @property
    def job_id(self) -> str:
        """
        The (unique) job identifier.
        """
        return self._job_id

    @property
    def service_id(self) -> str:
        """
        The (unique) service identifier of the instance of the file-writer that executes the current job.
        """
        return self._service_id

    @service_id.setter
    def service_id(self, new_service_id: str) -> None:
        if not self._service_id:
            self._service_id = new_service_id
            self._last_update = datetime.now()
        elif self._service_id == new_service_id:
            return
        else:
            raise RuntimeError(
                f'Can not set service_id of job with id "{self._job_id}" to "{new_service_id}" as it has already been set to "{self._service_id}".'
            )

    @property
    def last_update(self) -> datetime:
        """
        The local time stamp of the last update of the status of the job.
        """
        return self._last_update

    @property
    def state(self) -> JobState:
        """
        The current state of the job.
        """
        return self._state

    @property
    def file_name(self) -> str:
        """
        The file name of the job. None if the file name is not known.
        """
        if self._file_name == "":
            return None
        return self._file_name

    @file_name.setter
    def file_name(self, new_file_name: str) -> None:
        self._file_name = new_file_name
        self._last_update = datetime.now()

    @state.setter
    def state(self, new_state: JobState) -> None:
        self._state = new_state
        self._last_update = datetime.now()

    @property
    def message(self) -> str:
        """
        Status/state message of the job as received from the file-writer.
        """
        return self._message

    @property
    def metadata(self) -> Optional[Dict]:
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: Dict) -> None:
        self._metadata = metadata

    @message.setter
    def message(self, new_message: str) -> None:
        if new_message:
            self._message = new_message
            self._last_update = datetime.now()
