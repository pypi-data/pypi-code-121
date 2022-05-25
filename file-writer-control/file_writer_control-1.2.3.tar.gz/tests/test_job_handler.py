from datetime import datetime
from unittest.mock import Mock

import pytest

from file_writer_control.JobHandler import JobHandler
from file_writer_control.JobStatus import JobState, JobStatus
from file_writer_control.WriteJob import WriteJob


def test_default_members():
    worker_finder_mock = Mock()
    under_test = JobHandler(worker_finder_mock)
    assert under_test.job_id == ""
    assert under_test.worker_finder is worker_finder_mock


def test_start_job():
    test_job = WriteJob("{}", "some_file_name", "some_broker", datetime.now())
    worker_finder_mock = Mock()
    under_test = JobHandler(worker_finder_mock)
    assert (
        under_test.start_job(test_job) == worker_finder_mock.try_start_job.return_value
    )
    worker_finder_mock.try_start_job.assert_called_once_with(test_job)


def test_get_state_no_job_id():
    worker_finder_mock = Mock()
    under_test = JobHandler(worker_finder_mock)
    assert under_test.get_state() == worker_finder_mock.get_job_state.return_value
    worker_finder_mock.get_job_state.assert_called_once_with("")


def test_error_string_no_id():
    worker_finder_mock = Mock()
    test_job = WriteJob("{}", "some_file_name", "some_broker", datetime.now())
    worker_finder_mock.get_job_status.return_value = None
    under_test = JobHandler(worker_finder_mock)
    under_test.start_job(test_job)
    assert under_test.get_message() == ""
    worker_finder_mock.get_job_status.assert_called_once_with(test_job.job_id)


def test_error_string_with_id():
    worker_finder_mock = Mock()
    test_job = WriteJob("{}", "some_file_name", "some_broker", datetime.now())
    test_job_status = JobStatus(test_job.job_id)
    test_job_status.message = "test msg"
    worker_finder_mock.get_job_status.return_value = test_job_status
    under_test = JobHandler(worker_finder_mock)
    under_test.start_job(test_job)
    assert under_test.get_message() is test_job_status.message
    worker_finder_mock.get_job_status.assert_called_once_with(test_job.job_id)


def test_set_stop_time_no_id():
    worker_finder_mock = Mock()
    test_job = WriteJob("{}", "some_file_name", "some_broker", datetime.now())
    worker_finder_mock.get_job_status.return_value = None
    under_test = JobHandler(worker_finder_mock)
    under_test.start_job(test_job)
    test_stop_time = datetime.now()
    assert under_test.set_stop_time(test_stop_time) is None


def test_set_stop_time_with_id():
    worker_finder_mock = Mock()
    test_job = WriteJob("{}", "some_file_name", "some_broker", datetime.now())
    test_job_status = JobStatus(test_job.job_id)
    test_job_status.service_id = "some_service_id"
    worker_finder_mock.get_job_status.return_value = test_job_status
    under_test = JobHandler(worker_finder_mock)
    under_test.start_job(test_job)
    test_stop_time = datetime.now()
    assert (
        under_test.set_stop_time(test_stop_time)
        is worker_finder_mock.try_send_stop_time.return_value
    )
    worker_finder_mock.try_send_stop_time.assert_called_once_with(
        test_job_status.service_id, test_job.job_id, test_stop_time
    )


def test_abort_write_job_no_id():
    worker_finder_mock = Mock()
    test_job = WriteJob("{}", "some_file_name", "some_broker", datetime.now())
    worker_finder_mock.get_job_status.return_value = None
    under_test = JobHandler(worker_finder_mock)
    under_test.start_job(test_job)
    assert under_test.abort_write_job() is None


def test_abort_write_job_with_id():
    worker_finder_mock = Mock()
    test_job = WriteJob("{}", "some_file_name", "some_broker", datetime.now())
    test_job_status = JobStatus(test_job.job_id)
    test_job_status.service_id = "some_service_id"
    worker_finder_mock.get_job_status.return_value = test_job_status
    under_test = JobHandler(worker_finder_mock)
    under_test.start_job(test_job)
    assert (
        under_test.abort_write_job() is worker_finder_mock.try_send_abort.return_value
    )
    worker_finder_mock.try_send_abort.assert_called_once_with(
        test_job_status.service_id, test_job.job_id
    )


def test_is_not_done():
    worker_finder_mock = Mock()
    test_job = WriteJob("{}", "some_file_name", "some_broker", datetime.now())
    worker_finder_mock.get_job_state.return_value = JobState.ERROR
    under_test = JobHandler(worker_finder_mock)
    under_test.start_job(test_job)
    with pytest.raises(RuntimeError):
        under_test.is_done()
    assert worker_finder_mock.get_job_state.call_count >= 1


def test_timed_out():
    worker_finder_mock = Mock()
    test_job = WriteJob("{}", "some_file_name", "some_broker", datetime.now())
    worker_finder_mock.get_job_state.return_value = JobState.TIMEOUT
    under_test = JobHandler(worker_finder_mock)
    under_test.start_job(test_job)
    with pytest.raises(RuntimeError):
        under_test.is_done()
    assert worker_finder_mock.get_job_state.call_count >= 1


def test_is_done():
    worker_finder_mock = Mock()
    test_job = WriteJob("{}", "some_file_name", "some_broker", datetime.now())
    worker_finder_mock.get_job_state.return_value = JobState.DONE
    under_test = JobHandler(worker_finder_mock)
    under_test.start_job(test_job)
    assert under_test.is_done()
    worker_finder_mock.get_job_state.assert_called_once_with(test_job.job_id)
