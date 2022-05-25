from json import loads
from typing import Optional

from streaming_data_types.action_response_answ import (
    ActionOutcome,
    ActionResponse,
    ActionType,
)
from streaming_data_types.status_x5f2 import StatusMessage

from file_writer_control.CommandStatus import CommandState
from file_writer_control.JobStatus import JobState
from file_writer_control.WorkerStatus import WorkerState


def extract_worker_state_from_status(status: StatusMessage) -> WorkerState:
    """
    Determine the worker state (i.e. file-writer state) based on a file-writer status message.
    :param status: A status update message from a file-writer.
    :return: The extracted worker state.
    """
    json_struct = loads(status.status_json)
    status_map = {"writing": WorkerState.WRITING, "idle": WorkerState.IDLE}
    try:
        status_string = json_struct["state"]
        return status_map[status_string]
    except KeyError:
        return WorkerState.UNKNOWN


def extract_state_from_command_answer(answer: ActionResponse) -> CommandState:
    """
    Determine the command state from a action response message.
    :param answer: The action (either "start a job" or "set top time") response from a file-writer.
    :return: The extracted command state/response.
    """
    status_map = {
        ActionOutcome.Failure: CommandState.ERROR,
        ActionOutcome.Success: CommandState.SUCCESS,
    }
    try:
        return status_map[answer.outcome]
    except KeyError:
        return CommandState.ERROR


def extract_job_state_from_answer(answer: ActionResponse) -> Optional[JobState]:
    """
    Determine the file writing job state from a action response message.
    :param answer: The action (either "start a job" or "set top time") response from a file-writer.
    :return: The extracted job state, None if job state can not be determined from this answer.
    """
    if answer.action == ActionType.StartJob:
        if answer.outcome == ActionOutcome.Success:
            return JobState.WRITING
        else:
            return JobState.ERROR
    return None
