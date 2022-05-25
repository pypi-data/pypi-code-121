import pytest

from file_writer_control.CommandStatus import (
    CommandState,
    CommandStatus,
    COMMAND_STATUS_TIMEOUT,
)
from datetime import timedelta


def test_init():
    job_id = "some job id"
    command_id = "some command id"
    under_test1 = CommandStatus(job_id=job_id, command_id=command_id)
    assert under_test1.job_id == job_id
    assert under_test1.command_id == command_id
    assert under_test1.state == CommandState.NO_COMMAND


def test_eq_exception():
    under_test1 = CommandStatus("job_id", "command_id")
    with pytest.raises(NotImplementedError):
        under_test1 == 1


def test_eq_success():
    under_test1 = CommandStatus("job_id", "command_id")
    under_test2 = CommandStatus("job_id", "command_id")
    assert under_test1 == under_test2


def test_eq_failure_1():
    under_test1 = CommandStatus("job_id1", "command_id1")
    under_test2 = CommandStatus("job_id2", "command_id1")
    assert under_test1 != under_test2


def test_eq_failure_2():
    under_test1 = CommandStatus("job_id1", "command_id1")
    under_test2 = CommandStatus("job_id1", "command_id2")
    assert under_test1 != under_test2


def test_update_failure():
    under_test1 = CommandStatus("job_id1", "command_id1")
    under_test2 = CommandStatus("job_id1", "command_id2")
    with pytest.raises(RuntimeError):
        under_test2.update_status(under_test1)


def test_update_success():
    under_test1 = CommandStatus("job_id1", "command_id1")
    under_test2 = CommandStatus("job_id1", "command_id1")
    under_test2.update_status(under_test1)  # No exception


def test_timeout1():
    under_test = CommandStatus("job_id1", "command_id1")
    assert under_test.timeout == COMMAND_STATUS_TIMEOUT


def test_timeout2():
    test_time = timedelta(minutes=2)
    under_test = CommandStatus("job_id1", "command_id1", test_time)
    assert under_test.timeout == test_time
    test_time2 = timedelta(seconds=30)
    under_test.timeout = test_time2
    assert under_test.timeout == test_time2


def test_update_message():
    under_test1 = CommandStatus("job_id1", "command_id1")
    under_test2 = CommandStatus("job_id1", "command_id1")
    test_msg = "some test message"
    under_test1.message = test_msg
    assert under_test2.message == ""
    under_test2.update_status(under_test1)  # No exception
    assert under_test2.message == test_msg


def test_set_message():
    under_test1 = CommandStatus("job_id1", "command_id1")
    last_update = under_test1.last_update
    test_msg = "some test message"
    assert under_test1.message == ""
    under_test1.message = test_msg
    assert under_test1.message == test_msg
    assert under_test1.last_update != last_update


def test_set_state():
    under_test1 = CommandStatus("job_id1", "command_id1")
    last_update = under_test1.last_update
    test_state = CommandState.SUCCESS
    assert under_test1.state == CommandState.NO_COMMAND
    under_test1.state = test_state
    assert under_test1.state == test_state
    assert under_test1.last_update != last_update
