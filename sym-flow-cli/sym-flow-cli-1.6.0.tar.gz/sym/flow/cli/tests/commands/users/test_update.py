from unittest.mock import patch

import pytest

from sym.flow.cli.helpers.users import UserUpdateSet
from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.factories.users import UserFactory
from sym.flow.cli.tests.helpers.sandbox import Sandbox


@patch("sym.flow.cli.commands.users.list.click.edit")
class TestUsersUpdate:
    @pytest.fixture
    def users(self):
        yield UserFactory.create_batch(2)

    @pytest.fixture
    def services(self, users):
        yield [i.service for i in users[0].identities]

    @pytest.fixture(autouse=True)
    def fixture_patch(self, users, services):
        """Set up class-level patches using fixtures, since they can't be passed
        directly into patch decorators.
        """
        with patch("sym.flow.cli.helpers.api.SymAPI.get_users", return_value=users):
            with patch(
                "sym.flow.cli.helpers.api.SymAPI.get_services", return_value=services
            ):
                yield

    @patch("sym.flow.cli.commands.users.update.click.confirm", return_value=True)
    @patch("sym.flow.cli.commands.users.list.click.echo")
    @patch("sym.flow.cli.helpers.api_operations.OperationHelper.apply_changes")
    def test_click_calls_execution_method(
        self,
        mock_operation_apply_changes,
        mock_click_echo,
        mock_click_confirm,
        mock_click_edit,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(click_command, ["users", "update"])
            assert result.exit_code == 0

        mock_click_edit.assert_called_once()
        mock_operation_apply_changes.assert_called_once()

    @patch("sym.flow.cli.commands.users.list.click.echo")
    @patch("sym.flow.cli.helpers.api_operations.OperationHelper.apply_changes")
    def test_no_confirm_does_not_edit(
        self,
        mock_operation_apply_changes,
        mock_click_echo,
        mock_click_edit,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(click_command, ["users", "update"])
            assert result.exit_code == 1

        mock_click_edit.assert_not_called()
        mock_operation_apply_changes.assert_not_called()

    @patch("sym.flow.cli.commands.users.list.click.echo")
    @patch("sym.flow.cli.helpers.api_operations.OperationHelper.apply_changes")
    def test_file_input(
        self,
        mock_operation_apply_changes,
        mock_click_echo,
        mock_click_edit,
        click_setup,
        users,
        services,
        sandbox: Sandbox,
    ):
        filepath = f"{sandbox.path}/pytest.csv"
        UserUpdateSet(user_data=users, service_data=services).write_to_csv(filepath)

        with click_setup() as runner:
            result = runner.invoke(
                click_command, ["users", "update", "--input-file", filepath]
            )
            assert result.exit_code == 0

        mock_click_edit.assert_not_called()
        mock_operation_apply_changes.assert_called_once()

    @patch("sym.flow.cli.commands.users.update.click.confirm", return_value=True)
    @patch("sym.flow.cli.helpers.users.UserUpdateSet.add_csv_row")
    @patch("sym.flow.cli.helpers.api_operations.OperationHelper.apply_changes")
    def test_edit_the_correct_amount_of_users(
        self,
        mock_operation_apply_changes,
        mock_add_csv_row,
        mock_click_confirm,
        mock_click_edit,
        click_setup,
        users,
    ):
        with click_setup() as runner:
            result = runner.invoke(click_command, ["users", "update"])
            assert result.exit_code == 0

        assert mock_add_csv_row.call_count == len(users)
