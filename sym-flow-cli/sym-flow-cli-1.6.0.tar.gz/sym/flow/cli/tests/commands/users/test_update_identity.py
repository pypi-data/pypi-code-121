from unittest.mock import call, patch

import pytest

from sym.flow.cli.models.service_type import ServiceType
from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.factories.users import ServiceFactory, UserFactory


@patch("sym.flow.cli.helpers.api_operations.OperationHelper.handle_update_users")
class TestUsersUpdateIdentity:
    @pytest.fixture
    def users(self):
        yield UserFactory.create_batch(3)

    @pytest.fixture
    def services(self, users):
        # Create a second slack service
        slack2 = ServiceFactory.create(slug=ServiceType.SLACK.type_name)
        all_services = [
            i.service
            for i in users[0].identities
            if i.service.service_type != ServiceType.SYM.type_name
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

    def test_update_user_identity(self, mock_apply, click_setup, users):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "users",
                    "update-identity",
                    users[0].sym_email,
                    "--new-value",
                    "U123",
                    "--service-type",
                    "slack",
                    "--external-id",
                    "T12345",
                ],
            )
            assert result.exit_code == 0

    @pytest.mark.parametrize(
        "service_type, external_id, invalid_input, hints",
        [
            ("pagerduty", "unknown-id", "unknown-id", "pytest-pd"),  # bad external_id
            (
                "unknown-service",
                "T12345",
                "unknown-service",
                "aptible, aws_iam, aws_sso, github, okta, pagerduty, slack",
            ),  # bad service_type
            (
                "auth0",
                "T12345",
                "auth0",
                "aptible, aws_iam, aws_sso, github, okta, pagerduty, slack",
            ),  # service_type not registered with org
        ],
    )
    def test_update_user_identity_bad_input(
        self,
        mock_apply,
        service_type,
        external_id,
        invalid_input,
        hints,
        click_setup,
        users,
    ):
        with click_setup() as runner:
            # Test unknown external_id
            result = runner.invoke(
                click_command,
                [
                    "users",
                    "update-identity",
                    users[0].sym_email,
                    "--new-value",
                    "U123",
                    "--service-type",
                    service_type,
                    "--external-id",
                    external_id,
                ],
            )
            assert f"Invalid input: '{invalid_input}'" in result.output
            assert f"Try one of: {hints}" in result.output

    def test_update_user_identity_unknown_email(
        self,
        mock_apply,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["users", "update-identity", "someone@symops.io", "--new-value", "U123"],
            )
            assert "Unknown user for email: someone@symops.io" in result.output

    def test_update_user_identity_prompt_both(
        self, mock_apply, click_setup, users, services
    ):
        with click_setup() as runner:
            # Prompts both service type and external ID
            slack_external_ids = sorted(
                [
                    s.external_id
                    for s in services
                    if s.service_type == ServiceType.SLACK.type_name
                ]
            )

            with patch(
                "inquirer.list_input", side_effect=["slack", slack_external_ids[0]]
            ) as mock_inquire:
                result = runner.invoke(
                    click_command,
                    [
                        "users",
                        "update-identity",
                        users[0].sym_email,
                        "--new-value",
                        "U123",
                    ],
                )
                assert result.exit_code == 0

                mock_inquire.assert_has_calls(
                    [
                        call(
                            "Which service type?",
                            choices=sorted(list({s.service_type for s in services})),
                        ),
                        call("Which slack service?", choices=slack_external_ids),
                    ]
                )

    def test_update_user_identity_prompt_external_id(
        self, mock_apply, click_setup, users, services
    ):
        with click_setup() as runner:
            # Prompts external ID
            slack_external_ids = sorted(
                [
                    s.external_id
                    for s in services
                    if s.service_type == ServiceType.SLACK.type_name
                ]
            )
            with patch(
                "inquirer.list_input", side_effect=[slack_external_ids[0]]
            ) as mock_inquire:
                result = runner.invoke(
                    click_command,
                    [
                        "users",
                        "update-identity",
                        users[0].sym_email,
                        "--new-value",
                        "U123",
                        "--service-type",
                        "slack",
                    ],
                )
                assert result.exit_code == 0
                mock_inquire.assert_has_calls(
                    [call("Which slack service?", choices=slack_external_ids)]
                )

    def test_update_user_identity_prompt_service_type(
        self, mock_apply, click_setup, users, services
    ):
        with click_setup() as runner:
            # Prompts service type
            with patch("inquirer.list_input", side_effect=["slack"]) as mock_inquire:
                result = runner.invoke(
                    click_command,
                    [
                        "users",
                        "update-identity",
                        users[0].sym_email,
                        "--new-value",
                        "U123",
                        "--external-id",
                        "T12345",
                    ],
                )
                assert result.exit_code == 0
                mock_inquire.assert_has_calls(
                    [
                        call(
                            "Which service type?",
                            choices=sorted(list({s.service_type for s in services})),
                        )
                    ]
                )

    def test_update_user_identity_does_not_prompt_external_id(
        self, mock_apply, click_setup, users, services
    ):
        with click_setup() as runner:
            # Does not prompt external_id if there is only one service
            with patch("inquirer.list_input", side_effect=["pagerduty"]) as mock_inquire:
                result = runner.invoke(
                    click_command,
                    [
                        "users",
                        "update-identity",
                        users[0].sym_email,
                        "--new-value",
                        "U123",
                    ],
                )
                assert result.exit_code == 0
                mock_inquire.assert_has_calls(
                    [
                        call(
                            "Which service type?",
                            choices=sorted(list({s.service_type for s in services})),
                        )
                    ]
                )

                # Should print the auto-selected external ID
                assert "Which pagerduty service?: Using 'pytest-pd'" in result.output

    def test_update_user_identity_prompt_new_value(
        self, mock_apply, click_setup, users, services
    ):
        with click_setup() as runner:
            with patch("inquirer.text", return_value="P1234") as mock_inquire_text:
                result = runner.invoke(
                    click_command,
                    [
                        "users",
                        "update-identity",
                        users[0].sym_email,
                        "--service-type",
                        "slack",
                        "--external-id",
                        "T12345",
                    ],
                )
                assert result.exit_code == 0

                mock_inquire_text.assert_has_calls([call(message="New value?")])

    def test_update_user_identity_blank_value(
        self, mock_apply, click_setup, users, services
    ):
        with click_setup() as runner:
            with patch("inquirer.text", return_value="") as mock_inquire_text:
                result = runner.invoke(
                    click_command,
                    [
                        "users",
                        "update-identity",
                        users[0].sym_email,
                        "--service-type",
                        "slack",
                        "--external-id",
                        "T12345",
                    ],
                )
                assert result.exit_code != 0
                assert "Identity value cannot be empty" in result.output
