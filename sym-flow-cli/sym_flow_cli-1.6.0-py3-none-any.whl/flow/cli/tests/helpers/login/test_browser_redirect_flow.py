import json
import threading
import webbrowser
from unittest.mock import patch

import pkce
import pytest
import requests
from requests import Response
from sym.shared.cli.errors import CliError

from sym.flow.cli.errors import InvalidTokenError
from sym.flow.cli.helpers.login.login_flow import BrowserRedirectFlow, LoginError


@pytest.fixture
def browser_redirect_flow(mocker):
    flow = BrowserRedirectFlow(11001)
    mocker.patch.object(pkce, "generate_code_verifier", return_value="test-verifier")
    mocker.patch.object(pkce, "get_code_challenge", return_value="test-challenge")
    mocker.patch.object(webbrowser, "open")
    return flow


@pytest.fixture
def wait_for_code_tester(browser_redirect_flow, global_options):
    def fixture(expected_state: str, expected_code: str, do_test):
        def run_test():
            code = browser_redirect_flow.wait_for_code(expected_state, global_options)
            assert code == expected_code

        th = threading.Thread(target=run_test)
        th.start()
        do_test()
        th.join()

    return fixture


def test_redirect_uri(browser_redirect_flow):
    assert browser_redirect_flow.redirect_url == "http://localhost:11001/callback"


def test_get_auth_code(mocker, browser_redirect_flow, global_options, test_org):
    mocker.patch.object(browser_redirect_flow, "wait_for_code", return_value="1234XYZ")
    mocker.patch.object(browser_redirect_flow, "gen_state", return_value="foo")
    code, verifier = browser_redirect_flow.get_auth_code(global_options, test_org)
    assert code == "1234XYZ"
    assert verifier == "test-verifier"
    webbrowser.open.assert_called_once_with(
        f"https://auth.com/authorize?response_type=code&client_id={test_org['client_id']}&code_challenge_method=S256&code_challenge=test-challenge&redirect_uri=http://localhost:11001/callback&scope=admin offline_access&audience=https://api.symops.com&state=foo&prompt=login"
    )


@pytest.mark.skip(reason="flaky, causes circleci to hang sometimes")
def test_wait_for_code(wait_for_code_tester):
    def do_test():
        r = requests.get(
            "http://localhost:11001/callback?code=test_wait_for_code&state=foo"
        )
        assert r.status_code == 200
        assert "Login Successful!" in r.text

    wait_for_code_tester(
        expected_state="foo", expected_code="test_wait_for_code", do_test=do_test
    )


@pytest.mark.skip(reason="flaky, causes circleci to hang sometimes")
def test_wait_for_code_missing_code(wait_for_code_tester):
    def do_test():
        r = requests.get("http://localhost:11001/callback?state=foo")
        assert r.status_code == 401
        assert "Missing code in query" in r.text

    wait_for_code_tester(expected_state="foo", expected_code=None, do_test=do_test)


@pytest.mark.skip(reason="flaky, causes circleci to hang sometimes")
def test_wait_for_code_missing_state(wait_for_code_tester):
    def do_test():
        r = requests.get("http://localhost:11001/callback?code=test_wait_for_code")
        assert r.status_code == 401
        assert "Missing state in query" in r.text

    wait_for_code_tester(expected_state="", expected_code=None, do_test=do_test)


@pytest.mark.skip(reason="flaky, causes circleci to hang sometimes")
def test_wait_for_code_invalid_state(wait_for_code_tester):
    def do_test():
        r = requests.get(
            "http://localhost:11001/callback?code=test_wait_for_code&state=bar"
        )
        assert r.status_code == 401
        assert "Invalid state" in r.text

    wait_for_code_tester(expected_state="foo", expected_code=None, do_test=do_test)


def test_get_token_from_code_ok(mocker, browser_redirect_flow, global_options, test_org):
    response_json = json.loads(
        """
        {
        "access_token": "test-access-token",
        "token_type": "Bearer",
        "expires_in": "86400",
        "refresh_token": "test-refresh-token",
        "scope": "test-scope offline_access"
    }
    """
    )
    response = Response()
    response.status_code = 200

    mocker.patch.object(requests, "post", return_value=response)
    mocker.patch.object(response, "json", return_value=response_json)
    token = browser_redirect_flow.get_token_from_code(
        global_options, test_org, "1234XYZ", "test-verifier"
    )
    requests.post.assert_called_once_with(
        "https://auth.com/oauth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "client_id": test_org["client_id"],
            "code_verifier": "test-verifier",
            "code": "1234XYZ",
            "redirect_uri": "http://localhost:11001/callback",
        },
    )
    assert token["access_token"] == "test-access-token"
    assert token["refresh_token"] == "test-refresh-token"


def test_get_token_from_code_missing_refresh_token(
    mocker, browser_redirect_flow, global_options, test_org
):
    with pytest.raises(InvalidTokenError):
        response_json = json.loads(
            """
            {
            "access_token": "test-access-token",
            "token_type": "Bearer",
            "expires_in": "86400",
            "scope": "test-scope offline_access"
        }
        """
        )
        response = Response()
        response.status_code = 200
        mocker.patch.object(requests, "post", return_value=response)
        mocker.patch.object(response, "json", return_value=response_json)
        browser_redirect_flow.get_token_from_code(
            global_options, test_org, "1234XYZ", "test-verifier"
        )


def test_get_token_from_code_error_response(
    mocker, browser_redirect_flow, global_options, test_org
):
    with pytest.raises(LoginError):
        response = Response()
        response.status_code = 403
        mocker.patch.object(requests, "post", return_value=response)
        browser_redirect_flow.get_token_from_code(
            global_options, test_org, "1234XYZ", "test-verifier"
        )


def test_login(mocker, global_options, browser_redirect_flow, auth_token, test_org):
    mocker.patch.object(
        browser_redirect_flow,
        "get_auth_code",
        return_value=("test-code", "test-verifier"),
    )
    mocker.patch.object(
        browser_redirect_flow, "get_token_from_code", return_value=auth_token
    )
    token = browser_redirect_flow.login(global_options, test_org)
    assert token == auth_token
    browser_redirect_flow.get_auth_code.assert_called_once_with(global_options, test_org)
    browser_redirect_flow.get_token_from_code.assert_called_once_with(
        global_options, test_org, "test-code", "test-verifier"
    )


@patch(
    "sym.flow.cli.helpers.login.login_flow.BrowserRedirectFlow.get_auth_code",
    return_value=(None, None),
)
def test_login_no_auth_code(
    mock_get_auth_code, browser_redirect_flow, global_options, test_org
):
    with pytest.raises(CliError, match="Unable to get access token from Auth0"):
        browser_redirect_flow.login(global_options, test_org)

    mock_get_auth_code.assert_called_once()
