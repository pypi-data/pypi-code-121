from datetime import datetime
from unittest.mock import Mock

import pytest
from streaming_data_types.run_stop_6s4t import deserialise_6s4t as deserialise_stop

from file_writer_control.JobStatus import JobState, JobStatus
from file_writer_control.WorkerFinder import WorkerFinderBase
from file_writer_control.WriteJob import WriteJob


def test_send_command():
    cmd_channel_mock = Mock()
    producer_mock = Mock()
    test_topic = "some topic"
    under_test = WorkerFinderBase(test_topic, cmd_channel_mock, producer_mock)
    data_under_test = b"abcdefghijklmnopqrstwxyz"
    under_test.send_command(data_under_test)
    producer_mock.send.assert_called_once_with(test_topic, data_under_test)


def test_try_start_job():
    cmd_channel_mock = Mock()
    producer_mock = Mock()
    test_topic = "some topic"
    under_test = WorkerFinderBase(test_topic, cmd_channel_mock, producer_mock)
    with pytest.raises(NotImplementedError):
        under_test.try_start_job(WriteJob("", "", "", datetime.now()))


def test_try_send_stop_time():
    service_id = "some service_id"
    job_id = "some job id"
    cmd_channel_mock = Mock()
    producer_mock = Mock()
    test_topic = "some topic"
    stop_time = datetime.now()
    under_test = WorkerFinderBase(test_topic, cmd_channel_mock, producer_mock)
    result = under_test.try_send_stop_time(service_id, job_id, stop_time)
    cmd_channel_mock.add_command_id.assert_called_once_with(
        job_id=job_id, command_id=result.command_id
    )
    producer_mock.send.assert_called_once()
    topic_name = producer_mock.send.call_args_list[0].args[0]
    assert topic_name == test_topic
    message = deserialise_stop(producer_mock.send.call_args_list[0].args[1])
    assert message.service_id == service_id
    assert message.job_id == job_id
    assert message.command_id == result.command_id
    assert message.stop_time == int(stop_time.timestamp() * 1000)


def test_try_abort_job_now():
    service_id = "some service_id"
    job_id = "some job id"
    cmd_channel_mock = Mock()
    producer_mock = Mock()
    test_topic = "some topic"
    under_test = WorkerFinderBase(test_topic, cmd_channel_mock, producer_mock)
    result = under_test.try_send_abort(service_id, job_id)
    cmd_channel_mock.add_command_id.assert_called_once_with(
        job_id=job_id, command_id=result.command_id
    )
    producer_mock.send.assert_called_once()
    topic_name = producer_mock.send.call_args_list[0].args[0]
    assert topic_name == test_topic
    message = deserialise_stop(producer_mock.send.call_args_list[0].args[1])
    assert message.service_id == service_id
    assert message.job_id == job_id
    assert message.command_id == result.command_id


def test_get_job_status():
    job_id = "some job id"
    cmd_channel_mock = Mock()
    producer_mock = Mock()
    test_topic = "some topic"
    under_test = WorkerFinderBase(test_topic, cmd_channel_mock, producer_mock)
    result = under_test.get_job_status(job_id)
    cmd_channel_mock.get_job.assert_called_once_with(job_id)
    assert cmd_channel_mock.get_job.return_value == result


def test_get_job_state_success():
    job_id = "some job id"
    cmd_channel_mock = Mock()
    producer_mock = Mock()
    test_topic = "some topic"
    under_test = WorkerFinderBase(test_topic, cmd_channel_mock, producer_mock)
    used_state = JobStatus(job_id)
    used_state.state = JobState.TIMEOUT
    cmd_channel_mock.get_job.return_value = used_state
    result = under_test.get_job_state(job_id)
    cmd_channel_mock.get_job.assert_called_once_with(job_id)
    assert used_state.state == result


def test_get_job_state_failure():
    job_id = "some job id"
    cmd_channel_mock = Mock()
    producer_mock = Mock()
    test_topic = "some topic"
    under_test = WorkerFinderBase(test_topic, cmd_channel_mock, producer_mock)
    cmd_channel_mock.get_job.return_value = None
    result = under_test.get_job_state(job_id)
    cmd_channel_mock.get_job.assert_called_once_with(job_id)
    assert JobState.UNAVAILABLE == result


def test_list_commands():
    cmd_channel_mock = Mock()
    producer_mock = Mock()
    test_topic = "some topic"
    under_test = WorkerFinderBase(test_topic, cmd_channel_mock, producer_mock)
    assert (
        under_test.list_known_commands() == cmd_channel_mock.list_commands.return_value
    )


def test_list_jobs():
    cmd_channel_mock = Mock()
    producer_mock = Mock()
    test_topic = "some topic"
    under_test = WorkerFinderBase(test_topic, cmd_channel_mock, producer_mock)
    assert under_test.list_known_jobs() == cmd_channel_mock.list_jobs.return_value


def test_list_workers():
    cmd_channel_mock = Mock()
    producer_mock = Mock()
    test_topic = "some topic"
    under_test = WorkerFinderBase(test_topic, cmd_channel_mock, producer_mock)
    assert under_test.list_known_workers() == cmd_channel_mock.list_workers.return_value
