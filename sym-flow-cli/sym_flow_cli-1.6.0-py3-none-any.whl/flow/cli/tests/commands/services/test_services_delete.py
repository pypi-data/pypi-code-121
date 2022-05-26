from unittest.mock import call, patch

import pytest

from sym.flow.cli.models.service_type import ServiceType
from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.factories.users import ServiceFactory, UserFactory


class TestServicesDelete:
    @pytest.fixture
    def services(self):
        users = UserFactory.create_batch(3)
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
    def patchypatch(self, services):
        with patch("sym.flow.cli.helpers.api.SymAPI.get_services", return_value=services):
            yield

    @patch(
        "sym.flow.cli.helpers.api.SymAPI.get_service_references",
        return_value={"identities": [], "integrations": []},
    )
    @patch("sym.flow.cli.helpers.api.SymAPI.delete_service")
    @patch("sym.flow.cli.commands.services.services_delete.pre_service_delete_hooks")
    def test_services_delete(
        self,
        mock_pre_delete_hooks,
        mock_delete_service,
        mock_get_service_references,
        click_setup,
        services,
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "services",
                    "delete",
                    "--service-type",
                    services[0].service_type,
                    "--external-id",
                    services[0].external_id,
                ],
            )
            assert result.exit_code == 0
            assert (
                f"Successfully deleted service type slack with external ID {services[0].external_id}!"
                in result.output
            )
            mock_pre_delete_hooks.assert_called_once()
            mock_pre_delete_hooks.call_args.args[1] == services[0]
            mock_delete_service.assert_called_once()

    def test_services_delete_prompt_external_id(self, services, click_setup):
        with click_setup() as runner:
            with patch("inquirer.list_input") as mock_inquire:
                result = runner.invoke(
                    click_command,
                    ["services", "delete", "--service-type", "slack"],
                )

            slack_external_ids = sorted(
                [
                    s.external_id
                    for s in services
                    if s.service_type == ServiceType.SLACK.type_name
                ]
            )
            mock_inquire.assert_has_calls(
                [call("Which slack service?", choices=slack_external_ids)]
            )

    @patch("sym.flow.cli.helpers.api.SymAPI.delete_service")
    def test_services_delete_not_found_errors(self, mock_delete_service, click_setup):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "services",
                    "delete",
                    "--service-type",
                    "slack",
                    "--external-id",
                    "T123ABC",
                ],
            )
            mock_delete_service.assert_not_called()
            assert result.exit_code is not 0
            assert "Invalid input: 'T123ABC" in result.output
            assert "Try one of:" in result.output

    @patch(
        "sym.flow.cli.helpers.api.SymAPI.get_service_references",
        return_value={"identities": ["uuid1"], "integrations": ["uuid2"]},
    )
    @patch("sym.flow.cli.helpers.api.SymAPI.delete_service")
    @patch("sym.flow.cli.commands.services.services_delete.pre_service_delete_hooks")
    def test_services_delete_has_references(
        self,
        mock_pre_delete_hooks,
        mock_delete_service,
        mock_get_service_references,
        click_setup,
        services,
    ):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "services",
                    "delete",
                    "--service-type",
                    services[0].service_type,
                    "--external-id",
                    services[0].external_id,
                ],
            )
            mock_get_service_references.assert_called_once()
            mock_pre_delete_hooks.assert_not_called()
            mock_delete_service.assert_not_called()
            assert result.exit_code is not 0
            assert (
                f"Cannot perform delete because it is referenced by 1 identities and 1 integrations"
                in result.output
            )
