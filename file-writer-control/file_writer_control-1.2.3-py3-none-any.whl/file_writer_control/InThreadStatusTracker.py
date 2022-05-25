import json
from datetime import datetime, timedelta
from queue import Queue
from typing import Dict

from streaming_data_types import deserialise_6s4t as deserialise_stop_time
from streaming_data_types import deserialise_answ as deserialise_answer
from streaming_data_types import deserialise_pl72 as deserialise_start
from streaming_data_types import deserialise_wrdn as deserialise_stopped
from streaming_data_types import deserialise_x5f2 as deserialise_status
from streaming_data_types.action_response_answ import FILE_IDENTIFIER as ANSW_IDENTIFIER
from streaming_data_types.action_response_answ import Response
from streaming_data_types.finished_writing_wrdn import (
    FILE_IDENTIFIER as STOPPED_IDENTIFIER,
)
from streaming_data_types.finished_writing_wrdn import WritingFinished
from streaming_data_types.run_start_pl72 import FILE_IDENTIFIER as START_IDENTIFIER
from streaming_data_types.run_start_pl72 import RunStartInfo
from streaming_data_types.run_stop_6s4t import FILE_IDENTIFIER as STOP_TIME_IDENTIFIER
from streaming_data_types.run_stop_6s4t import RunStopInfo
from streaming_data_types.status_x5f2 import FILE_IDENTIFIER as STAT_IDENTIFIER
from streaming_data_types.status_x5f2 import StatusMessage
from streaming_data_types.utils import get_schema

from file_writer_control.CommandStatus import CommandState, CommandStatus
from file_writer_control.JobStatus import JobState, JobStatus
from file_writer_control.StateExtractor import (
    extract_job_state_from_answer,
    extract_state_from_command_answer,
    extract_worker_state_from_status,
)
from file_writer_control.WorkerStatus import WorkerState, WorkerStatus

DEAD_ENTITY_TIME_LIMIT = timedelta(hours=1)


class InThreadStatusTracker:
    """
    Implements de-coding of flatbuffer messages and sends updates of worker, job and command state/status back to the
    "main"-thread if there has been changes.
    """

    def __init__(self, status_queue: Queue):
        """
        Constructor.
        :param status_queue: The output queue to which state/status updates are pushed.
        """
        self.queue = status_queue
        self.known_workers: Dict[str, WorkerStatus] = {}
        self.known_jobs: Dict[str, JobStatus] = {}
        self.known_commands: Dict[str, CommandStatus] = {}

    def process_message(self, message: bytes):
        """
        Process a binary message.
        :param message: The binary message to be processed.
        """
        current_schema = get_schema(message).encode("utf-8")
        update_time = datetime.now()
        msg_process_map = {
            ANSW_IDENTIFIER: lambda msg: self.process_answer(deserialise_answer(msg)),
            STAT_IDENTIFIER: lambda msg: self.process_status(deserialise_status(msg)),
            STOP_TIME_IDENTIFIER: lambda msg: self.process_set_stop_time(
                deserialise_stop_time(msg)
            ),
            START_IDENTIFIER: lambda msg: self.process_start(deserialise_start(msg)),
            STOPPED_IDENTIFIER: lambda msg: self.process_stopped(
                deserialise_stopped(msg)
            ),
        }
        if current_schema in msg_process_map:
            msg_process_map[current_schema](message)

        self.send_status_if_updated(update_time)

    def send_status_if_updated(self, limit_time: datetime):
        """
        Sends status updates of workers, jobs and commands (to the status queue) if there has been any updates on or
        after the limit_time.
        :param limit_time: The cut-off time for deciding which updates should be sent to the status queue.
        """
        for entity in (
            list(self.known_workers.values())
            + list(self.known_jobs.values())
            + list(self.known_commands.values())
        ):
            if entity.last_update >= limit_time:
                self.queue.put(entity)

    def check_for_worker_presence(self, service_id: str):
        """
        Check if a service_id is known and add it to a list of known ones if it is not.
        :param service_id: The service identifier to look for.
        """
        if service_id not in self.known_workers:
            self.known_workers[service_id] = WorkerStatus(service_id)

    def check_for_job_presence(self, job_id: str):
        """
        Check if a job identifier is known and add it to a list of known ones if it is not.
        :param job_id: The job identifier to look for.
        """
        if job_id not in self.known_jobs:
            new_job = JobStatus(job_id)
            self.known_jobs[job_id] = new_job

    def check_for_command_presence(self, job_id: str, command_id: str):
        """
        Check if a command identifier is known and add it to a list of known ones if it is not.
        :param job_id: The job identifier of the command that we are looking for. (Only used if we need to add the
        command.)
        :param command_id: The command identifier to look for.
        """
        if command_id not in self.known_commands:
            new_command = CommandStatus(job_id, command_id)
            self.known_commands[command_id] = new_command

    def check_for_lost_connections(self):
        """
        Check workers, commands and jobs for the last update time and change the state of these if a timeout has been
        reached.
        """
        now = datetime.now()
        for entity in (
            list(self.known_workers.values())
            + list(self.known_jobs.values())
            + list(self.known_commands.values())
        ):
            entity.check_if_outdated(now)
        self.send_status_if_updated(now)

    def prune_dead_entities(self, current_time: datetime):
        """
        Will remove old jobs, workers and commands that have not been updated recently.
        :return:
        """

        def pruner(entities_dictionary):
            for key in list(entities_dictionary.keys()):
                if (
                    entities_dictionary[key].last_update + DEAD_ENTITY_TIME_LIMIT
                    < current_time
                ):
                    del entities_dictionary[key]

        pruner(self.known_workers)
        pruner(self.known_commands)
        pruner(self.known_jobs)

    def process_answer(self, answer: Response):
        """
        Update workers, jobs and commands based on information in a response message.
        :param answer: The response/answer message to use for status updates.
        """
        self.check_for_worker_presence(answer.service_id)
        self.check_for_job_presence(answer.job_id)
        self.check_for_command_presence(answer.job_id, answer.command_id)
        new_job_state = extract_job_state_from_answer(answer)
        if new_job_state is not None:
            self.known_jobs[answer.job_id].state = new_job_state
        current_command = self.known_commands[answer.command_id]
        current_command.state = extract_state_from_command_answer(answer)
        current_command.message = answer.message
        current_command.response_code = Response.status_code
        self.known_jobs[answer.job_id].message = answer.message
        self.known_jobs[answer.job_id].service_id = answer.service_id

    def process_status(self, status_update: StatusMessage):
        """
        Update workers and jobs based on information in a status message.
        :param status_update: The status message to use for updates.
        """
        self.check_for_worker_presence(status_update.service_id)
        current_state = extract_worker_state_from_status(status_update)
        self.known_workers[status_update.service_id].state = current_state
        if current_state == WorkerState.WRITING:
            try:
                json_data = json.loads(status_update.status_json)
                job_id = json_data["job_id"]
            except (KeyError, json.JSONDecodeError):
                raise RuntimeError("Unable to extract JSON data from status message.")
            file_name = json_data["file_being_written"]
            self.check_for_job_presence(job_id)
            self.known_jobs[job_id].state = JobState.WRITING
            self.known_jobs[job_id].file_name = file_name
            self.known_jobs[job_id].metadata = json_data
            # For some jobs, we will only know the service-id when a worker starts working on a job.
            # Thus we need the following statement to update the (known) service-id of a job.
            try:
                self.known_jobs[job_id].service_id = status_update.service_id
            except RuntimeError:
                pass  # Expected error (i.e. the job is not known), do nothing

    def process_set_stop_time(self, stop_time: RunStopInfo):
        """
        Update commands and jobs based on information in a "set stop time" message.
        :param stop_time: The "stop" message to use for updates.
        """
        self.check_for_command_presence(stop_time.job_id, stop_time.command_id)
        self.known_commands[stop_time.command_id].state = CommandState.WAITING_RESPONSE

    def process_start(self, start: RunStartInfo):
        """
        Update commands and jobs based on information in a "start" message.
        :param start: The "start" message to use for updates.
        """
        self.check_for_job_presence(start.job_id)
        self.check_for_command_presence(start.job_id, start.job_id)
        self.known_commands[start.job_id].state = CommandState.WAITING_RESPONSE

    def process_stopped(self, stopped: WritingFinished):
        """
        Update workers and jobs based on information in a "has stopped" message.
        :param stopped: The "stopped" message to use for updates.
        """
        self.check_for_job_presence(stopped.job_id)
        self.check_for_worker_presence(stopped.service_id)
        current_job = self.known_jobs[stopped.job_id]
        if stopped.error_encountered:
            current_job.state = JobState.ERROR
        else:
            current_job.state = JobState.DONE
            current_job.metadata = json.loads(stopped.metadata)
        current_job.message = stopped.message
        self.known_workers[stopped.service_id].state = WorkerState.IDLE
