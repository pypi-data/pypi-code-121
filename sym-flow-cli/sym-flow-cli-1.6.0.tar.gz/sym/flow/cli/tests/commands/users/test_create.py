from unittest.mock import call, patch

import pytest

from sym.flow.cli.commands.users.create import prompt_for_identity
from sym.flow.cli.models.service_type import ServiceType
from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.factories.users import ServiceFactory, UserFactory


@patch("sym.flow.cli.helpers.api_operations.OperationHelper.handle_update_users")
class TestUsersCreate:
    @pytest.fixture
    def users(self):
        yield UserFactory.create_batch(3)

    @pytest.fixture
    def services(self, users):
        # Create a second slack service
        slack2 = ServiceFactory.create(slug=ServiceType.SLACK.type_name)
        all_services = [
            i.service for i in users[0].identities if i.service.service_type
        ] + [slack2]

        # User Factory creates the same services for each user
        yield all_services

    @pytest.fixture(autouse=True)
    def patchypatch(self, users, services):
        with patch("sym.flow.cli.helpers.api.SymAPI.get_users", return_value=users):
            with patch(
                "sym.flow.cli.helpers.api.SymAPI.get_services", return_value=services
            ):
                yield

    def test_create_blank_user(self, mock_apply, click_setup, users):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "users",
                    "create",
                    "foo_bar@symops.io",
                ],
            )
            assert result.exit_code == 0

    def test_create_user_existing_email(self, mock_apply, click_setup, users):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["users", "create", users[0].sym_email],
            )
            assert (
                f"A user already exists with email: {users[0].sym_email}" in result.output
            )

    def test_create_user_prompt_identity(self, mock_apply, click_setup, users, services):
        with click_setup() as runner:
            with patch(
                "inquirer.text",
                side_effect=["U123", "U456"],  # two slack services, should inquire twice
            ) as mock_inquire:
                result = runner.invoke(
                    click_command,
                    [
                        "users",
                        "create",
                        "foo_bar@symops.io",
                        "-s",
                        "slack",
                    ],
                )
                assert result.exit_code == 0
                expected_calls = [
                    call(f"Slack ({s.external_id}) {ServiceType.SLACK.matcher}")
                    for s in services
                    if s.service_type == ServiceType.SLACK.type_name
                ]
                mock_inquire.assert_has_calls(expected_calls, any_order=True)

    def test_create_user_unknown_service(
        self,
        mock_apply,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "users",
                    "create",
                    "foo_bar@symops.io",
                    "-s",
                    "something-bad",
                ],
            )
            assert "Invalid input: 'something-bad'" in result.output
            mock_apply.assert_not_called()

    def test_create_user_not_registered_service(
        self,
        mock_apply,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "users",
                    "create",
                    "foo_bar@symops.io",
                    "-s",
                    "google",  # factory does not create an google service
                ],
            )
            assert "No service is registered for type google" in result.output
            assert (
                "You can create the service with `symflow services create --service-type google`"
                in result.output
            )
            mock_apply.assert_not_called()

    @patch("inquirer.text", return_value="  ")
    def test_prompt_for_identity_skips_blank_input(self, mock_inquirer, mock_apply):
        service = ServiceFactory.create(slug=ServiceType.SLACK.type_name)
        result = prompt_for_identity(ServiceType.get(service.service_type), service)  # type: ignore
        expected_calls = [
            call(f"Slack ({service.external_id}) {ServiceType.SLACK.matcher}")
        ]
        mock_inquirer.assert_has_calls(expected_calls)

        assert result is None
