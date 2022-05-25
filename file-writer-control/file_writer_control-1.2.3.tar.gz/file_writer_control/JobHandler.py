from datetime import datetime
from typing import Union

from file_writer_control.CommandHandler import CommandHandler
from file_writer_control.JobStatus import JobState
from file_writer_control.WorkerFinder import WorkerFinder
from file_writer_control.WriteJob import WriteJob


class JobHandler:
    """
    A stand in for controlling and checking the state of a job running on a file-writer instance.
    """

    def __init__(self, worker_finder: WorkerFinder, job_id=""):
        """
        Constructor.
        :param worker_finder: An instance of a class that inherits from WorkerFinder and implements the member function
        try_start_job of that class.
        :param job_id: (Optional) The job identifier of an existing job.
        """
        self.worker_finder = worker_finder
        self._job_id = job_id

    def start_job(self, job: WriteJob) -> CommandHandler:
        """
        Start a write job. This call is not blocking. It does not guarantee that the write job will actually be started.
        :param job: The write to be started.
        .. note:: Starting a new job will cause the current instance of this class to no longer being able to track or
        control previous jobs.
        :return: A CommandHandler instance that can be used to monitor the outcome of the attempt to start a write job.
        """
        self._job_id = job.job_id
        return self.worker_finder.try_start_job(job)

    def get_state(self) -> JobState:
        """
        Get the state of the job.
        """
        return self.worker_finder.get_job_state(self._job_id)

    def is_done(self) -> bool:
        """
        :return: True if job was completed without errors. False otherwise.
        .. note:: If the job was completed with errors, this call will return False.
        """
        current_job_state = self.worker_finder.get_job_state(self._job_id)
        if current_job_state == JobState.ERROR:
            raise RuntimeError(f'Job failed with error message "{self.get_message()}".')
        if current_job_state == JobState.TIMEOUT:
            raise RuntimeError("Timed out while trying to start write job.")
        return current_job_state == JobState.DONE

    def get_message(self) -> str:
        """
        Get a string describing the error that was encountered when running the job. (If there was an error.)
        """
        current_status = self.worker_finder.get_job_status(self._job_id)
        if current_status is None:
            return ""
        return current_status.message

    def set_stop_time(self, stop_time: datetime) -> Union[CommandHandler, None]:
        """
        Set a new stop time for the file-writing job. There is no guarantee that the stop time will actually be changed.
        This call is not blocking. Calling this member function will have no effect on the stop-time before the write
        job has started.

        :param stop_time: The new stop time of the job.
        :return: A CommandHandler instance that can be used to monitor the outcome of the attempt to set a new stop time.
        """
        current_status = self.worker_finder.get_job_status(self._job_id)
        if current_status is None:
            return None
        return self.worker_finder.try_send_stop_time(
            current_status.service_id, self._job_id, stop_time
        )

    def stop_now(self) -> Union[CommandHandler, None]:
        """
        See the documentation for abort_write_job().
        """
        return self.abort_write_job()

    def abort_write_job(self) -> Union[CommandHandler, None]:
        """
        Tell the file-writing to abort writing. There is no guarantee that will actually happen though.
        This call is not blocking. Calling this member function will have no effect if done before a write job has
        actually started.

        :return: A CommandHandler instance that can be used to monitor the outcome of the attempt to set a new stop time.
        """
        current_status = self.worker_finder.get_job_status(self._job_id)
        if current_status is None:
            return None
        return self.worker_finder.try_send_abort(
            current_status.service_id, self._job_id
        )

    @property
    def job_id(self) -> str:
        """
        The job identifier of the job that this instance of the JobHandler class represent.
        """
        return self._job_id
