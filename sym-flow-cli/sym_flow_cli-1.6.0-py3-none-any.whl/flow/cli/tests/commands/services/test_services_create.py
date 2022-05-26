from unittest.mock import patch

import pytest

from sym.flow.cli.errors import NotAuthorizedError
from sym.flow.cli.models.service import Service
from sym.flow.cli.models.service_type import MANAGED_SERVICES, ServiceType
from sym.flow.cli.symflow import symflow as click_command


class TestServicesCreate:

    EXTERNAL_ID_INPUTS = {
        ServiceType.SLACK: "T123ABC",
        ServiceType.AWS_SSO: "arn:aws:sso:::instance/",
        ServiceType.AWS_IAM: "123456789012",
    }
    BAD_EXTERNAL_ID_INPUTS = {
        ServiceType.SLACK: ["T123abc", "123ABC"],  # not all upper, doesn't start with T
        ServiceType.AWS_SSO: ["instance/"],  # invalid arn
        ServiceType.AWS_IAM: ["1234abc"],  # not 12 digits
    }

    MOCK_SLACK_SERVICE = Service(
        id="fake-uuid", slug="slack", external_id="T123ABC", label="Slack"
    )

    @patch(
        "sym.flow.cli.helpers.api.SymAPI.create_service", return_value=MOCK_SLACK_SERVICE
    )
    @patch("sym.flow.cli.commands.services.services_create.post_service_create_hooks")
    def test_services_create(
        self, mock_post_service_create_hooks, mock_create_service, click_setup
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "services",
                    "create",
                    "--service-type",
                    self.MOCK_SLACK_SERVICE.service_type,
                    "--external-id",
                    self.MOCK_SLACK_SERVICE.external_id,
                ],
            )
            assert result.exit_code == 0
            assert (
                f"Successfully set up service type slack with external ID {self.MOCK_SLACK_SERVICE.external_id}!"
                in result.output
            )
            mock_create_service.assert_called_once()
            mock_post_service_create_hooks.assert_called_once()
            mock_post_service_create_hooks.call_args.args[1] == self.MOCK_SLACK_SERVICE

    @pytest.mark.parametrize(
        "service_type",
        [s.value for s in ServiceType if s.type_name not in MANAGED_SERVICES],
    )
    def test_services_create_prompt_external_id(self, service_type, click_setup):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["services", "create", "--service-type", service_type.type_name],
                input="^C",
            )
            # Check that the printed external ID is the one associated with the given service_type
            assert service_type.external_id_name in result.output

    @pytest.mark.parametrize(
        "service_type", [s.value for s in ServiceType if s.validator]
    )
    @patch("sym.flow.cli.helpers.api.SymAPI.create_service")
    def test_services_create_validation(
        self, mock_create_service, service_type, click_setup
    ):
        with click_setup() as runner:
            # Ensure that the validator is called if it is defined on a the service type
            # Example input must be defined in self.EXTERNAL_ID_INPUTS
            external_id = self.EXTERNAL_ID_INPUTS[service_type]
            result = runner.invoke(
                click_command,
                ["services", "create", "--service-type", service_type.type_name],
                input=external_id,
            )
            assert result.exit_code == 0

    @pytest.mark.parametrize(
        "service_type", [s.value for s in ServiceType if s.validator]
    )
    @patch("sym.flow.cli.helpers.api.SymAPI.create_service")
    def test_services_create_validation_failure(
        self, mock_create_service, service_type, click_setup
    ):
        with click_setup() as runner:
            # Ensure that the help_str is displayed on validation failure
            # Example input must be defined in self.BAD_EXTERNAL_ID_INPUTS
            for external_id in self.BAD_EXTERNAL_ID_INPUTS[service_type]:
                result = runner.invoke(
                    click_command,
                    ["services", "create", "--service-type", service_type.type_name],
                    input=external_id,
                )

                assert service_type.help_str in result.output
                assert result.exit_code != 0

    @patch(
        "sym.flow.cli.helpers.api.SymAPI.create_service",
        side_effect=NotAuthorizedError,
    )
    def test_services_create_not_authorized_errors(
        self, mock_create_service, click_setup
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "services",
                    "create",
                    "--service-type",
                    "slack",
                    "--external-id",
                    "T123ABC",
                ],
            )
            mock_create_service.assert_called_once()
            assert result.exit_code is not 0
