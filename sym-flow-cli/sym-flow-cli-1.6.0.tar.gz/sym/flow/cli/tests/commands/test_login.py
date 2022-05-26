from typing import List, Union, cast
from unittest.mock import patch

import pytest
from sym.shared.cli.errors import CliError

from sym.flow.cli.errors import InvalidTokenError, LoginError
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.helpers.login.login_flow import LoginFlow
from sym.flow.cli.models import AuthToken, Organization
from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.conftest import get_mock_response

TEST_LOGIN_EMAIL = "ci@symops.io"


def mock_login_flow(result: Union[AuthToken, CliError]):
    class MockLoginFlow(LoginFlow):
        def login(self, options: GlobalOptions, org: Organization) -> AuthToken:
            # TypedDict doesn't support isinstance
            if isinstance(result, dict):
                return result
            raise cast(CliError, result)

        def gen_browser_login_params(self, options: GlobalOptions, org: Organization):
            return ("", None, None)

    return MockLoginFlow()


@pytest.fixture
def login_flow(auth_token):
    return mock_login_flow(auth_token)


@pytest.fixture
def login_flow_login_error():
    return mock_login_flow(LoginError("test"))


@pytest.fixture
def login_flow_invalid_token_error():
    return mock_login_flow(InvalidTokenError("test"))


login_test_org = Organization(slug="test", client_id="12345abc")


@pytest.fixture
def login_tester(click_setup):
    def tester(
        login_flow: LoginFlow,
        email: str,
        expected_output: List[str],
        success: bool = True,
    ):
        with patch.object(LoginFlow, "get_login_flow", return_value=login_flow):
            with click_setup() as runner:
                result = runner.invoke(click_command, ["login", "--email", email])
                print(result.output)
                for expected_str in expected_output:
                    assert expected_str in result.output
                if success:
                    assert result.exit_code == 0
                else:
                    assert result.exit_code != 0

    return tester


@patch(
    "sym.flow.cli.helpers.api.SymAPI.get_organization_from_email",
    return_value=login_test_org,
)
@patch(
    "sym.flow.cli.helpers.api.SymAPI.verify_login",
    return_value=True,
)
def test_login_ok(mock_verify_login, mock_get_org, login_flow, login_tester):
    expected_output = ["Org: test", "Login succeeded"]
    login_tester(
        login_flow=login_flow,
        email=TEST_LOGIN_EMAIL,
        success=True,
        expected_output=expected_output,
    )

    mock_get_org.assert_called_once_with(TEST_LOGIN_EMAIL)
    mock_verify_login.assert_called_once_with(TEST_LOGIN_EMAIL)


@patch(
    "sym.flow.cli.helpers.api.SymAPI.get_organization_from_email",
    return_value=login_test_org,
)
def test_login_login_error(mock_get_org, login_flow_login_error, login_tester):
    expected_output = [
        "Org: test",
        "Error logging in: test",
    ]
    login_tester(
        login_flow=login_flow_login_error,
        email=TEST_LOGIN_EMAIL,
        success=False,
        expected_output=expected_output,
    )


@patch(
    "sym.flow.cli.helpers.api.SymAPI.get_organization_from_email",
    return_value=login_test_org,
)
def test_login_invalid_token_error(
    mock_get_org, login_flow_invalid_token_error, login_tester
):
    expected_output = [
        "Org: test",
        "Unable to parse token: test",
    ]
    login_tester(
        login_flow=login_flow_invalid_token_error,
        email=TEST_LOGIN_EMAIL,
        success=False,
        expected_output=expected_output,
    )


@patch(
    "sym.flow.cli.helpers.api.SymRESTClient.get",
    return_value=(get_mock_response(200)),
)
def test_login_unknown_org(mock_api_get, login_flow, login_tester):
    expected_output = [
        f"Unknown organization for email: {TEST_LOGIN_EMAIL}",
    ]
    login_tester(
        login_flow=login_flow,
        email=TEST_LOGIN_EMAIL,
        success=False,
        expected_output=expected_output,
    )


@patch(
    "sym.flow.cli.helpers.api.SymAPI.get_organization_from_email",
    return_value=login_test_org,
)
def test_login_api_verify_failure(mock_get_org, login_flow, login_tester):
    expected_output = ["Sym could not verify this login"]

    with patch(
        "sym.flow.cli.helpers.api.SymAPI.verify_login",
        return_value=False,
    ) as mock_verify_failed:
        login_tester(
            login_flow=login_flow,
            email=TEST_LOGIN_EMAIL,
            success=True,  # Return code should only be non-zero if a truly unexpected error occurred
            expected_output=expected_output,
        )

        mock_verify_failed.assert_called_once_with(TEST_LOGIN_EMAIL)

    mock_get_org.assert_called_once()
