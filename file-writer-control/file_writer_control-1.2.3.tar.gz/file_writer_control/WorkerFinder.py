import uuid
from datetime import datetime
from typing import List

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from streaming_data_types.run_stop_6s4t import serialise_6s4t as serialise_stop

from file_writer_control.CommandChannel import CommandChannel
from file_writer_control.CommandHandler import CommandHandler
from file_writer_control.CommandStatus import CommandStatus
from file_writer_control.JobStatus import JobState, JobStatus
from file_writer_control.KafkaTopicUrl import KafkaTopicUrl
from file_writer_control.WorkerStatus import WorkerStatus
from file_writer_control.WriteJob import WriteJob


class WorkerFinderBase:
    def __init__(
        self,
        command_topic: str,
        command_channel: CommandChannel,
        message_producer: KafkaProducer,
    ):
        """
        Constructor.
        """
        self.command_channel = command_channel
        self.command_topic = command_topic
        self.message_producer = message_producer

    def send_command(self, message: bytes):
        """
        Send a message (command) to the file-writer "command"-topic.
        :param message: The command/message as binary data.
        """
        self.message_producer.send(self.command_topic, message)

    def try_start_job(self, job: WriteJob) -> CommandHandler:
        """
        Attempts to start a file-writing job. This function is not blocking. No guarantees are given that the job will
        be successfully started.
        .. note:: This class must be implemented by the classes inheriting from this one.
        :param job: The file-writing job to be started.
        :return: A CommandHandler instance for (more) easily checking the outcome of attempting to start a write job.
        """
        raise NotImplementedError("Not implemented in base class.")

    def try_send_stop_time(
        self, service_id: str, job_id: str, stop_time: datetime
    ) -> CommandHandler:
        """
        Sends a "set stop time" message to a file-writer running a job as identified by the parameters.
        This function is not blocking. No guarantees are given that this command will be followed.
        :param service_id: The service identifier of the file-writer to receive the command.
        :param job_id: The job identifier of the currently running file-writer job.
        :param stop_time: The new stop time.
        :return: A CommandHandler instance for (more) easily checking the outcome of setting a new stop time.
        """
        command_id = str(uuid.uuid1())
        message = serialise_stop(
            job_id=job_id,
            service_id=service_id,
            command_id=command_id,
            stop_time=stop_time,
        )
        self.command_channel.add_command_id(job_id=job_id, command_id=command_id)
        self.send_command(message)
        return CommandHandler(self.command_channel, command_id)

    def try_send_stop_now(self, service_id: str, job_id: str) -> CommandHandler:
        """
        See documentation for `try_send_abort()`.
        """
        return self.try_send_abort(service_id, job_id)

    def try_send_abort(self, service_id: str, job_id: str) -> CommandHandler:
        """
        Sends a "abort" message to a file-writer running a job as identified by the parameters of this function.
        This function is not blocking. No guarantees are given that this command will be followed.
        :param service_id: The service identifier of the file-writer to receive the command.
        :param job_id: The job identifier of the currently running file-writer job.
        :return: A CommandHandler instance for (more) easily checking the outcome of the "abort" command.
        """
        return self.try_send_stop_time(service_id, job_id, 0)

    def list_known_workers(self) -> List[WorkerStatus]:
        """
        :return: A list of the (known) status of the workers publishing status updates to the configured command topic.
        """
        return self.command_channel.list_workers()

    def list_known_jobs(self) -> List[JobStatus]:
        """
        :return: A list of the (known) jobs and their status as published on the configured command topic.
        """
        return self.command_channel.list_jobs()

    def list_known_commands(self) -> List[CommandStatus]:
        """
        :return: A list of the (known) commands and their outcomes as published on the configured command topic.
        """
        return self.command_channel.list_commands()

    def get_job_state(self, job_id: str) -> JobState:
        """
        Get the state of a specific job.
        :param job_id: The (unique) identifier of the job that we are trying to find the state of.
        :return: The state of the job if known, JobState.UNAVAILABLE if job is not known.
        """
        current_job = self.command_channel.get_job(job_id)
        if current_job is None:
            return JobState.UNAVAILABLE
        return current_job.state

    def get_job_status(self, job_id: str) -> JobStatus:
        """
        Get the full (known) status of a specific job.
        :param job_id: The (unique) identifier of the job that we are trying to find the status of.
        :return: The status of the job if known. None if it is not.
        """
        return self.command_channel.get_job(job_id)


class WorkerFinder(WorkerFinderBase):
    def __init__(self, command_topic_url: str):
        temp_cmd_ch = CommandChannel(command_topic_url)
        command_url = KafkaTopicUrl(command_topic_url)
        try:
            temp_producer = KafkaProducer(bootstrap_servers=[command_url.host_port])
        except NoBrokersAvailable as e:
            raise NoBrokersAvailable(
                f'Unable to find brokers (or connect to brokers) on address: "{command_url.host_port}"'
            ) from e
        super().__init__(command_url.topic, temp_cmd_ch, temp_producer)
