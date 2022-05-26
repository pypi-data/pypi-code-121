from unittest.mock import patch

from sym.flow.cli.helpers.config import store_login_config
from sym.flow.cli.symflow import symflow as click_command

EMAIL = "yasyf@symops.io"


def test_status_logged_out(click_setup):
    with click_setup() as runner:
        result = runner.invoke(click_command, ["status"])
        assert "are not currently logged in" in result.output
        assert result.exit_code == 1


@patch(
    "sym.flow.cli.helpers.api.SymAPI.verify_login",
    return_value=False,
)
def test_status_expired(mock_verify_login, click_setup, test_org, auth_token):
    with click_setup() as runner:
        store_login_config(EMAIL, test_org, auth_token)
        result = runner.invoke(click_command, ["status"])
        assert "Token expired" in result.output
        assert result.exit_code == 1


@patch(
    "sym.flow.cli.helpers.api.SymAPI.verify_login",
    return_value=True,
)
def test_status_success(mock_verify_login, click_setup, test_org, auth_token):
    with click_setup() as runner:
        store_login_config(EMAIL, test_org, auth_token)
        result = runner.invoke(click_command, ["status"])
        assert result.exit_code == 0
