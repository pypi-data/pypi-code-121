from unittest.mock import call, patch

import pytest

from sym.flow.cli.models.service_type import ServiceType
from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.factories.users import (
    BotUserFactory,
    IdentityFactory,
    ServiceFactory,
)


@patch("sym.flow.cli.helpers.api_operations.OperationHelper.handle_delete_identities")
class TestBotsDeleteIdentity:
    @pytest.fixture
    def bots(self):
        bots = BotUserFactory.create_batch(3)
        bots[0].identities.append(
            IdentityFactory(
                service__slug=ServiceType.SLACK.type_name,
                service__external_id="T12345",
                matcher={"user_id": "U12345"},
            )
        )
        bots[0].identities.append(
            IdentityFactory(
                service__slug=ServiceType.PAGERDUTY.type_name,
                service__external_id="pytest-pd",
                matcher={"user_id": "PD123"},
            )
        )
        yield bots

    @pytest.fixture
    def services(self, bots):
        # Create a second slack service
        slack2 = ServiceFactory.create(slug=ServiceType.SLACK.type_name)
        all_services = [
            i.service
            for i in bots[0].identities
            if i.service.service_type != ServiceType.SYM.type_name
        ] + [slack2]

        yield all_services

    @pytest.fixture(autouse=True)
    def patchypatch(self, bots, services):
        with patch("sym.flow.cli.helpers.api.SymAPI.get_users", return_value=bots):
            with patch(
                "sym.flow.cli.helpers.api.SymAPI.get_services", return_value=services
            ):
                yield

    def test_delete_bot_identity(self, mock_apply, click_setup, bots):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "bots",
                    "delete-identity",
                    bots[0].sym_identifier,
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
                "pagerduty, slack",
            ),  # bad service_type
            (
                "okta",
                "T12345",
                "okta",
                "pagerduty, slack",
            ),  # service_type not registered with org
        ],
    )
    def test_delete_bot_identity_bad_input(
        self,
        mock_apply,
        service_type,
        external_id,
        invalid_input,
        hints,
        click_setup,
        bots,
    ):
        with click_setup() as runner:
            # Test unknown external_id
            result = runner.invoke(
                click_command,
                [
                    "bots",
                    "delete-identity",
                    bots[0].sym_identifier,
                    "--service-type",
                    service_type,
                    "--external-id",
                    external_id,
                ],
            )
            assert f"Invalid input: '{invalid_input}'" in result.output
            assert f"Try one of: {hints}" in result.output

    def test_delete_bot_identity_unknown(
        self,
        mock_apply,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["bots", "delete-identity", "thesearenotthedroidsyourelookingfor"],
            )
            assert "Unknown bot: thesearenotthedroidsyourelookingfor" in result.output

    def test_delete_bot_identity_prompt_both(
        self, mock_apply, click_setup, bots, services
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
                        "bots",
                        "delete-identity",
                        bots[0].sym_identifier,
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

    def test_delete_bot_identity_prompt_external_id(
        self, mock_apply, click_setup, bots, services
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
                        "bots",
                        "delete-identity",
                        bots[0].sym_identifier,
                        "--service-type",
                        "slack",
                    ],
                )
                assert result.exit_code == 0

                mock_inquire.assert_has_calls(
                    [call("Which slack service?", choices=slack_external_ids)]
                )

    def test_delete_bot_identity_prompt_service_type(
        self, mock_apply, click_setup, bots, services
    ):
        with click_setup() as runner:
            # Prompts service type
            with patch("inquirer.list_input", side_effect=["slack"]) as mock_inquire:
                result = runner.invoke(
                    click_command,
                    [
                        "bots",
                        "delete-identity",
                        bots[0].sym_identifier,
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

    def test_delete_bot_identity_does_not_prompt_external_id(
        self, mock_apply, click_setup, bots, services
    ):
        with click_setup() as runner:
            # Does not prompt external_id if there is only one service
            with patch("inquirer.list_input", side_effect=["pagerduty"]) as mock_inquire:
                result = runner.invoke(
                    click_command,
                    [
                        "bots",
                        "delete-identity",
                        bots[0].sym_identifier,
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
