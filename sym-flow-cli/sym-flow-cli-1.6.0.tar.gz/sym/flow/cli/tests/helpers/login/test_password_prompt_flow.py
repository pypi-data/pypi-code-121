import json
import webbrowser

import pytest
import requests
from requests import Response

from sym.flow.cli.errors import InvalidTokenError
from sym.flow.cli.helpers.login.login_flow import LoginError, PasswordPromptFlow
from sym.flow.cli.models import UserCredentials


@pytest.fixture
def password_prompt_flow(mocker):
    flow = PasswordPromptFlow("test@symops.io")
    mocker.patch.object(webbrowser, "open")
    return flow


@pytest.fixture
def user_creds():
    return UserCredentials("username", "password")


def test_login_with_user_creds(
    mocker, global_options, password_prompt_flow, user_creds, test_org
):
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
    token = password_prompt_flow.login_with_user_creds(
        global_options,
        user_creds,
        test_org,
    )
    requests.post.assert_called_once_with(
        "https://auth.com/oauth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "http://auth0.com/oauth/grant-type/password-realm",
            "realm": "Username-Password-Authentication",
            "username": "username",
            "password": "password",
            "audience": "https://api.com",
            "scope": "admin offline_access",
            "client_id": test_org["client_id"],
        },
    )

    assert token["access_token"] == "test-access-token"
    assert token["refresh_token"] == "test-refresh-token"


def test_login_with_user_creds_no_refresh_token(
    mocker, global_options, password_prompt_flow, user_creds, test_org
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
        password_prompt_flow.login_with_user_creds(
            global_options,
            user_creds,
            test_org,
        )


def test_login_with_user_creds_error_response(
    mocker, global_options, password_prompt_flow, user_creds, test_org
):
    with pytest.raises(LoginError):
        response = Response()
        response.status_code = 403
        mocker.patch.object(requests, "post", return_value=response)
        password_prompt_flow.login_with_user_creds(
            global_options,
            user_creds,
            test_org,
        )


def test_login(
    mocker, global_options, password_prompt_flow, user_creds, auth_token, test_org
):
    mocker.patch.object(
        password_prompt_flow, "prompt_for_user_credentials", return_value=user_creds
    )
    mocker.patch.object(
        password_prompt_flow, "login_with_user_creds", return_value=auth_token
    )
    token = password_prompt_flow.login(global_options, test_org)
    assert token == auth_token
    password_prompt_flow.prompt_for_user_credentials.assert_called_once_with(
        "test@symops.io"
    )
    password_prompt_flow.login_with_user_creds.assert_called_once_with(
        global_options, user_creds, test_org
    )
