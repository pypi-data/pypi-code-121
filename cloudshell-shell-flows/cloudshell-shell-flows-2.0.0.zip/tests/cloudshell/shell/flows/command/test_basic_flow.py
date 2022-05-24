import unittest
from unittest import mock

from cloudshell.shell.flows.command.basic_flow import RunCommandFlow


class TestRunCommandFlow(unittest.TestCase):
    def setUp(self):
        self.logger = mock.MagicMock()
        self.cli_configurator = mock.MagicMock()
        self.enable_session = mock.MagicMock()
        self.config_session = mock.MagicMock()
        self.cli_configurator = mock.MagicMock(
            enable_mode_service=mock.MagicMock(
                return_value=mock.MagicMock(
                    __enter__=mock.MagicMock(return_value=self.enable_session)
                )
            ),
            config_mode_service=mock.MagicMock(
                return_value=mock.MagicMock(
                    __enter__=mock.MagicMock(return_value=self.config_session)
                )
            ),
        )
        self.run_flow = RunCommandFlow(
            logger=self.logger, cli_configurator=self.cli_configurator
        )

    def test_run_custom_command(self):
        custom_command = "test custom command"
        expected_result = mock.MagicMock()
        self.run_flow._run_command_flow = mock.MagicMock(return_value=expected_result)
        # act
        result = self.run_flow.run_custom_command(custom_command)
        # verify
        self.run_flow._run_command_flow.assert_called_once_with(
            custom_command=custom_command
        )
        self.assertEqual(result, expected_result)

    def test_run_custom_config_command(self):
        custom_command = "test custom config command"
        expected_result = mock.MagicMock()
        self.run_flow._run_command_flow = mock.MagicMock(return_value=expected_result)
        # act
        result = self.run_flow.run_custom_config_command(custom_command)
        # verify
        self.run_flow._run_command_flow.assert_called_once_with(
            custom_command=custom_command, is_config=True
        )
        self.assertEqual(result, expected_result)

    def test_parse_custom_commands(self):
        # act
        result = self.run_flow.parse_custom_commands(
            command="test command1;test command2"
        )
        # verify
        self.assertEqual(result, ["test command1", "test command2"])

    def test_run_command_flow(self):
        custom_command = "test custom command"
        expected_cmd_response = "test command response"
        self.enable_session.send_command.return_value = expected_cmd_response
        # act
        result = self.run_flow._run_command_flow(custom_command=custom_command)
        # verify
        self.enable_session.send_command.assert_called_once_with(command=custom_command)
        self.assertEqual(result, expected_cmd_response)

    def test_run_command_flow_in_config_mode(self):
        custom_command = "test custom config command"
        expected_cmd_response = "test command response"
        self.config_session.send_command.return_value = expected_cmd_response
        # act
        result = self.run_flow._run_command_flow(
            custom_command=custom_command, is_config=True
        )
        # verify
        self.config_session.send_command.assert_called_once_with(command=custom_command)
        self.assertEqual(result, expected_cmd_response)
