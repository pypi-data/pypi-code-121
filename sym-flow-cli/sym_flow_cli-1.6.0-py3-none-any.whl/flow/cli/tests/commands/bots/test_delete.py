from unittest.mock import patch

from sym.flow.cli.symflow import symflow as click_command


class TestBotsDelete:
    @patch("sym.flow.cli.helpers.api.SymAPI.delete_user")
    def test_delete(
        self,
        mock_delete_user,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(click_command, ["bots", "delete", "bot-user"])
            assert result.exit_code == 0
            assert "Successfully deleted bot user bot-user!" in result.output

        mock_delete_user.assert_called_once()

    @patch("sym.flow.cli.helpers.api.SymAPI.delete_user")
    def test_delete_missing_arguments(
        self,
        mock_delete_user,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(click_command, ["bots", "delete"])
            assert result.exit_code == 2

        mock_delete_user.assert_not_called()
