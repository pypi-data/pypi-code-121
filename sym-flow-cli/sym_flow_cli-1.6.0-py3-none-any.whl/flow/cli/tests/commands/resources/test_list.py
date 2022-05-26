from unittest.mock import patch

from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.factories.resources import TerraformResourceFactory


class TestResourcesList:
    @patch("sym.flow.cli.helpers.api.SymAPI.get_resources", return_value=[])
    def test_list_no_resources_exits(self, _, click_setup):
        with click_setup() as runner:
            result = runner.invoke(click_command, ["resources", "list", "sym_flow"])

        assert result.exit_code == 0
        assert "No sym_flow resources were found." in result.output

    def test_list_invalid_type_errors(self, click_setup):
        with click_setup() as runner:
            result = runner.invoke(click_command, ["resources", "list", "doggo"])

        assert result.exit_code != 0
        assert "Invalid input: 'doggo'" in result.output
        assert "sym_flow, sym_target" in result.output

    def test_list_resources_with_type(self, click_setup):
        resources = [
            TerraformResourceFactory.create(),
            TerraformResourceFactory.create(type="permission_context"),
            TerraformResourceFactory.create(),
            TerraformResourceFactory.create(type="pagerduty"),
        ]

        with patch(
            "sym.flow.cli.helpers.api.SymAPI.get_resources", return_value=resources
        ):
            with click_setup() as runner:
                result = runner.invoke(
                    click_command, ["resources", "list", "sym_integration"]
                )

        assert result.exit_code == 0
        assert "Type\n" in result.output  # Ensure the table header exists
        assert "pagerduty" in result.output  # Ensure row includes type value
        for resource in resources:
            assert resource.srn in result.output

    def test_list_resources_without_type(self, click_setup):
        resources = TerraformResourceFactory.create_batch(5)
        for r in resources:
            r.sub_type = None

        with patch(
            "sym.flow.cli.helpers.api.SymAPI.get_resources", return_value=resources
        ):
            with click_setup() as runner:
                result = runner.invoke(click_command, ["resources", "list", "sym_flow"])

        assert result.exit_code == 0
        assert "Type" not in result.output  # Ensure the table header does not exist
        assert resources[4].slug in result.output
        for resource in resources:
            assert resource.srn in result.output
