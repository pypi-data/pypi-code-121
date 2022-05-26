import uuid
from unittest.mock import patch

from sym.flow.cli.commands.services.hooks.slack_delete import slack_delete
from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.constants import DEFAULT_API_URL


class TestSlackDeleteHook:
    """Suite for testing Slack uninstallation."""

    @patch("sym.flow.cli.helpers.api.SymAPI.uninstall_slack")
    @patch("sym.flow.cli.commands.services.hooks.slack_delete.click.echo")
    def test_click_calls_uninstall_method_and_echoes(
        self, mock_click_echo, mock_slack_uninstall
    ):
        fake_service_id = str(uuid.uuid4())
        slack_delete(SymAPI(DEFAULT_API_URL), fake_service_id)

        mock_slack_uninstall.assert_called_once_with(fake_service_id)
        mock_click_echo.assert_called_once_with(
            "Uninstall successful! The Sym App has been removed from your Slack workspace."
        )
