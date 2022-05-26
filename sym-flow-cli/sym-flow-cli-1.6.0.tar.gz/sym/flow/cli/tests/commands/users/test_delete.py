from unittest.mock import patch

from sym.flow.cli.symflow import symflow as click_command


class TestUsersDelete:
    @patch("sym.flow.cli.commands.users.list.click.echo")
    @patch("sym.flow.cli.helpers.api.SymAPI.delete_user")
    def test_delete(
        self,
        mock_delete_user,
        mock_click_echo,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command, ["users", "delete", "sym", "--user-id", "user@symops.io"]
            )
            assert result.exit_code == 0

        mock_delete_user.assert_called_once()

    @patch("sym.flow.cli.commands.users.list.click.echo")
    @patch("sym.flow.cli.helpers.api.SymAPI.delete_user")
    def test_delete_missing_arguments(
        self,
        mock_delete_user,
        mock_click_echo,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command, ["users", "delete", "--user-id", "user@symops.io"]
            )
            assert result.exit_code == 2

    @patch("sym.flow.cli.commands.users.list.click.echo")
    @patch("sym.flow.cli.helpers.api.SymAPI.delete_user")
    def test_delete_unmapped_service(
        self,
        mock_delete_user,
        mock_click_echo,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["users", "delete", "unknown", "--user-id", '{"id": "user@symops.io"}'],
            )
            assert result.exit_code == 0

        mock_delete_user.assert_called_once()

    @patch("sym.flow.cli.commands.users.list.click.echo")
    @patch("sym.flow.cli.helpers.api.SymAPI.delete_user")
    def test_delete_unmapped_service_invalid_json(
        self,
        mock_delete_user,
        mock_click_echo,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["users", "delete", "unknown", "--user-id", "user@symops.io"],
            )
            assert result.exit_code == 1
            assert isinstance(result.exception, ValueError)
