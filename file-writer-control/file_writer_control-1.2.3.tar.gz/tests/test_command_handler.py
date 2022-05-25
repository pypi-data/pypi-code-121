from unittest.mock import Mock

import pytest

from file_writer_control.CommandHandler import CommandHandler
from file_writer_control.CommandStatus import CommandState, CommandStatus


def test_get_state_no_id():
    mock_cmd_ch = Mock()
    mock_cmd_ch.get_command.return_value = None
    cmd_id = "some_command_id"
    under_test = CommandHandler(mock_cmd_ch, cmd_id)
    assert under_test.get_state() == CommandState.UNKNOWN
    mock_cmd_ch.get_command.assert_called_once_with(cmd_id)


def test_get_state_with_id():
    mock_cmd_ch = Mock()
    job_id = "some_job_id"
    cmd_id = "some_command_id"
    stand_in_status = CommandStatus(job_id, cmd_id)
    mock_cmd_ch.get_command.return_value = stand_in_status
    under_test = CommandHandler(mock_cmd_ch, cmd_id)
    assert under_test.get_state() == stand_in_status.state
    mock_cmd_ch.get_command.assert_called_once_with(cmd_id)


def test_get_error_no_id():
    mock_cmd_ch = Mock()
    mock_cmd_ch.get_command.return_value = None
    cmd_id = "some_command_id"
    under_test = CommandHandler(mock_cmd_ch, cmd_id)
    assert under_test.get_message() == ""
    mock_cmd_ch.get_command.assert_called_once_with(cmd_id)


def test_get_error_with_id():
    mock_cmd_ch = Mock()
    job_id = "some_job_id"
    cmd_id = "some_command_id"
    message_string = "some message"
    stand_in_status = CommandStatus(job_id, cmd_id)
    stand_in_status.message = message_string
    mock_cmd_ch.get_command.return_value = stand_in_status
    under_test = CommandHandler(mock_cmd_ch, cmd_id)
    assert under_test.get_message() == message_string
    mock_cmd_ch.get_command.assert_called_once_with(cmd_id)


def test_has_timed_out():
    mock_cmd_ch = Mock()
    job_id = "some_job_id"
    cmd_id = "some_command_id"
    stand_in_status = CommandStatus(job_id, cmd_id)
    stand_in_status.state = CommandState.TIMEOUT_RESPONSE
    mock_cmd_ch.get_command.return_value = stand_in_status
    under_test = CommandHandler(mock_cmd_ch, cmd_id)
    with pytest.raises(RuntimeError):
        under_test.is_done()
    mock_cmd_ch.get_command.assert_called_once_with(cmd_id)


def test_is_not_done():
    mock_cmd_ch = Mock()
    job_id = "some_job_id"
    cmd_id = "some_command_id"
    stand_in_status = CommandStatus(job_id, cmd_id)
    stand_in_status.state = CommandState.ERROR
    mock_cmd_ch.get_command.return_value = stand_in_status
    under_test = CommandHandler(mock_cmd_ch, cmd_id)
    with pytest.raises(RuntimeError):
        under_test.is_done()
    assert mock_cmd_ch.get_command.call_count >= 1


def test_is_done():
    mock_cmd_ch = Mock()
    job_id = "some_job_id"
    cmd_id = "some_command_id"
    stand_in_status = CommandStatus(job_id, cmd_id)
    stand_in_status.state = CommandState.SUCCESS
    mock_cmd_ch.get_command.return_value = stand_in_status
    under_test = CommandHandler(mock_cmd_ch, cmd_id)
    assert under_test.is_done()
    mock_cmd_ch.get_command.assert_called_once_with(cmd_id)
