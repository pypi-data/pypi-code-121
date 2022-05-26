from unittest.mock import patch

import pytest

from sym.flow.cli.commands.users.list import get_user_data
from sym.flow.cli.errors import NotAuthorizedError
from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.constants import DEFAULT_API_URL
from sym.flow.cli.helpers.users import UserUpdateSet
from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.factories.users import UserFactory

COMMAND_PATH = "sym.flow.cli.commands.users.list"


class TestUsersList:
    @pytest.fixture
    def user_update_set(self) -> UserUpdateSet:
        yield UserUpdateSet(user_data=UserFactory.create_batch(2))

    @patch(f"{COMMAND_PATH}.click.echo")
    @patch(f"{COMMAND_PATH}.tabulate_user_data", return_value="some data")
    def test_command_echoes_tabulated_data_without_file_path(
        self, mock_tabulate, mock_click_echo, click_setup, user_update_set
    ):
        with patch(
            "sym.flow.cli.commands.users.list.get_user_data", return_value=user_update_set
        ) as mock_get_user:
            with click_setup() as runner:
                result = runner.invoke(click_command, ["users", "list"])
                assert result.exit_code == 0

        mock_get_user.assert_called_once()
        mock_tabulate.assert_called_once_with(user_update_set)
        mock_click_echo.assert_called_once_with("some data")

    @patch(f"{COMMAND_PATH}.click.echo")
    @patch(f"{COMMAND_PATH}.tabulate_user_data", return_value="some data")
    @patch("sym.flow.cli.helpers.users.UserUpdateSet.write_to_csv")
    def test_command_saves_to_file_with_file_path(
        self,
        mock_write_to_csv,
        mock_tabulate,
        mock_click_echo,
        click_setup,
        user_update_set,
    ):
        with patch(
            "sym.flow.cli.commands.users.list.get_user_data", return_value=user_update_set
        ) as mock_get_user:
            with click_setup() as runner:
                result = runner.invoke(
                    click_command, ["users", "list", "--output-file", "pytest.csv"]
                )
                assert result.exit_code == 0

        mock_get_user.assert_called_once()
        mock_write_to_csv.assert_called_once_with("pytest.csv")
        mock_tabulate.assert_not_called()
        mock_click_echo.assert_called_once_with("Saved 2 users to pytest.csv.")

    @patch(
        f"{COMMAND_PATH}.get_user_data",
        side_effect=ValueError("random error"),
    )
    def test_click_call_catches_unknown_error(
        self, mock_get_integration_data, click_setup
    ):
        with click_setup() as runner:
            result = runner.invoke(click_command, ["users", "list"])
            assert result.exit_code == 1
            assert isinstance(result.exception, ValueError)
            assert str(result.exception) == "random error"

        mock_get_integration_data.assert_called_once()

    @patch(
        "sym.flow.cli.helpers.api.SymAPI.get_users",
        side_effect=NotAuthorizedError,
    )
    def test_users_list_not_authorized_errors(
        self,
        mock_get_users,
    ):
        with pytest.raises(NotAuthorizedError, match="symflow login"):
            get_user_data(SymAPI("http://fake.symops.com/api/v1"))
        mock_get_users.assert_called_once()
