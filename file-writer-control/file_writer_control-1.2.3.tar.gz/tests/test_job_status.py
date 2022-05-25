import pytest

from file_writer_control.JobStatus import JobState, JobStatus


def test_update_status_exception():
    under_test1 = JobStatus("Some_id1")
    under_test2 = JobStatus("Some_id2")
    with pytest.raises(RuntimeError):
        under_test1.update_status(under_test2)


def test_update_status_success():
    under_test1 = JobStatus("Some_id1")
    assert under_test1.message == ""
    test_message = "some test message"
    under_test2 = JobStatus("Some_id1")
    under_test2.message = test_message
    under_test1.update_status(under_test2)  # No exception
    assert under_test1.message == test_message


def test_set_service_id():
    under_test1 = JobStatus("Some_id1")
    assert under_test1.service_id == ""
    test_service_id = "some service id"
    old_last_update = under_test1.last_update
    under_test1.service_id = test_service_id
    assert old_last_update != under_test1.last_update
    assert under_test1.service_id == test_service_id
    with pytest.raises(RuntimeError):
        under_test1.service_id = "some other service id"


def test_set_message():
    under_test1 = JobStatus("Some_id1")
    test_message = "some message"
    assert under_test1.message == ""
    last_update = under_test1.last_update
    under_test1.message = test_message
    assert under_test1.message == test_message
    assert last_update != under_test1.last_update


def test_set_state():
    under_test1 = JobStatus("Some_id1")
    test_state = JobState.ERROR
    last_update = under_test1.last_update
    assert under_test1.state == JobState.WAITING
    under_test1.state = test_state
    assert under_test1.state == test_state
    assert last_update != under_test1.last_update
