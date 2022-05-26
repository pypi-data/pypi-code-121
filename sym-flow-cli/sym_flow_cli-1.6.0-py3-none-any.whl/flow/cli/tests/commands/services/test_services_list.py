from unittest.mock import patch

import pytest

from sym.flow.cli.commands.services.services_list import get_services_data
from sym.flow.cli.errors import NotAuthorizedError
from sym.flow.cli.helpers.constants import DEFAULT_API_URL
from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.conftest import get_mock_response
from sym.flow.cli.tests.helpers.test_api import MOCK_SERVICES_DATA

MOCK_SERVICES_OUTPUT_STR = """
Service Type    External ID    Label
--------------  -------------  -------
google          symops.io      Google
sym             cloud          Sym
""".strip()


class TestServicesList:
    @patch("sym.flow.cli.commands.services.services_list.click.echo")
    @patch(
        "sym.flow.cli.commands.services.services_list.get_services_data",
        return_value="real data",
    )
    def test_click_calls_execution_method(
        self,
        mock_get_services_data,
        mock_click_echo,
        click_setup,
    ):
        with click_setup() as runner:
            result = runner.invoke(click_command, ["services", "list"])
            assert result.exit_code == 0

        mock_get_services_data.assert_called_once()
        mock_click_echo.assert_called_once_with("real data")

    @patch(
        "sym.flow.cli.commands.services.services_list.get_services_data",
        side_effect=ValueError("random error"),
    )
    def test_click_call_catches_unknown_error(self, mock_get_services_data, click_setup):
        with click_setup() as runner:
            result = runner.invoke(click_command, ["services", "list"])
            assert result.exit_code == 1
            assert isinstance(result.exception, ValueError)
            assert str(result.exception) == "random error"

        mock_get_services_data.assert_called_once()

    @patch(
        "sym.flow.cli.helpers.api.SymAPI.get_services",
        side_effect=NotAuthorizedError,
    )
    def test_services_list_not_authorized_errors(self, mock_get_services, global_options):
        with pytest.raises(NotAuthorizedError, match="symflow login"):
            get_services_data(global_options.sym_api)
        mock_get_services.assert_called_once()

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.get",
        return_value=(get_mock_response(200, data=MOCK_SERVICES_DATA)),
    )
    def test_services_list(self, mock_get_services, global_options):
        data = get_services_data(global_options.sym_api)
        assert data == MOCK_SERVICES_OUTPUT_STR
