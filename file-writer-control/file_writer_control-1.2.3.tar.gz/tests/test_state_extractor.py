from datetime import datetime

import pytest
from streaming_data_types.action_response_answ import (
    ActionOutcome,
    ActionType,
    Response,
)
from streaming_data_types.status_x5f2 import StatusMessage

from file_writer_control.CommandStatus import CommandState
from file_writer_control.JobStatus import JobState
from file_writer_control.StateExtractor import (
    extract_job_state_from_answer,
    extract_state_from_command_answer,
    extract_worker_state_from_status,
)
from file_writer_control.WorkerStatus import WorkerState


@pytest.mark.parametrize(
    "status_input,state",
    [
        ('{"state":"writing"}', WorkerState.WRITING),
        ('{"state":"idle"}', WorkerState.IDLE),
        ('{"state":"some_state"}', WorkerState.UNKNOWN),
    ],
)
def test_get_worker_state(status_input, state):
    message = StatusMessage(
        "name",
        "version",
        "service_id",
        "host_name",
        "process_id",
        update_interval=5,
        status_json=status_input,
    )
    assert extract_worker_state_from_status(message) == state


@pytest.mark.parametrize(
    "status_input,state",
    [
        (ActionOutcome.Success, CommandState.SUCCESS),
        (ActionOutcome.Failure, CommandState.ERROR),
        (12, CommandState.ERROR),
    ],
)
def test_get_state_from_command_answer(status_input, state):
    answer = Response(
        "service_id",
        "job_id",
        "command_id",
        ActionType.SetStopTime,
        status_input,
        "some message",
        1234,
        datetime.now(),
    )
    assert extract_state_from_command_answer(answer) == state


@pytest.mark.parametrize(
    "action,outcome,state",
    [
        (ActionType.SetStopTime, ActionOutcome.Success, None),
        (ActionType.StartJob, ActionOutcome.Success, JobState.WRITING),
        (ActionType.SetStopTime, ActionOutcome.Failure, None),
        (ActionType.StartJob, ActionOutcome.Failure, JobState.ERROR),
    ],
)
def test_get_job_state_from_answer_done(action, outcome, state):
    answer = Response(
        "service_id",
        "job_id",
        "command_id",
        action,
        outcome,
        "some message",
        1234,
        datetime.now(),
    )
    assert extract_job_state_from_answer(answer) is state
