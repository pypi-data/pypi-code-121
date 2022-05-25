import pytest

from file_writer_control.WorkerStatus import WorkerState, WorkerStatus


def test_init():
    test_id = "some_id"
    under_test1 = WorkerStatus(test_id)
    assert test_id == under_test1.service_id
    assert under_test1.state == WorkerState.UNAVAILABLE


def test_eq_wrong_type():
    under_test1 = WorkerStatus("some_id")
    with pytest.raises(NotImplementedError):
        under_test1 == 1


def test_eq_true():
    under_test1 = WorkerStatus("some_id")
    under_test2 = WorkerStatus("some_id")
    assert under_test1 == under_test2


def test_eq_false():
    under_test1 = WorkerStatus("some_id")
    under_test2 = WorkerStatus("some_id2")
    assert under_test1 != under_test2


def test_update_status_wrong_id():
    under_test1 = WorkerStatus("some_id")
    under_test2 = WorkerStatus("some_id2")
    with pytest.raises(RuntimeError):
        under_test1.update_status(under_test2)


def test_update_status_ok():
    test_state = WorkerState.WRITING
    under_test1 = WorkerStatus("some_id")
    under_test1.state = WorkerState.IDLE
    under_test2 = WorkerStatus("some_id")
    under_test2.state = test_state
    last_update = under_test1.last_update
    under_test1.update_status(under_test2)  # No throw
    assert last_update != under_test1.last_update
    assert under_test1.state == test_state


def test_state_change_date_change():
    under_test1 = WorkerStatus("some_id")
    last_update = under_test1.last_update
    under_test1.state = WorkerState.WRITING
    assert last_update != under_test1.last_update
