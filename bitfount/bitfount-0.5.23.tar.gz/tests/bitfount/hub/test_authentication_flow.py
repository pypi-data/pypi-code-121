"""Tests for the authentication mechanism."""
from datetime import datetime, timezone
import functools
import json
from pathlib import Path
from typing import Dict, Literal, Optional, Union, cast
from unittest.mock import Mock, call

from _pytest.capture import CaptureFixture
from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from dateutil.relativedelta import relativedelta
import jwt
import pytest
from pytest import fixture, raises
from pytest_lazyfixture import lazy_fixture
from pytest_mock import MockerFixture
import responses

from bitfount import web_utils
from bitfount.config import (
    _DEVELOPMENT_ENVIRONMENT,
    _PRODUCTION_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
)
from bitfount.hub.authentication_flow import (
    _AUTHORIZATION_PENDING_ERROR,
    _DEVELOPMENT_AUTH_DOMAIN,
    _DEVELOPMENT_CLIENT_ID,
    _DEVICE_CODE_GRANT_TYPE,
    _PRODUCTION_AUTH_DOMAIN,
    _PRODUCTION_CLIENT_ID,
    _SLOW_DOWN_ERROR,
    _STAGING_AUTH_DOMAIN,
    _STAGING_CLIENT_ID,
    _USERNAME_KEY,
    BitfountSession,
    _AuthEnv,
    _get_auth_environment,
)
from bitfount.hub.types import (
    _DeviceAccessTokenRequestDict,
    _DeviceAccessTokenResponseJSON,
    _DeviceCodeRequestDict,
    _DeviceCodeResponseJSON,
    _TokenRefreshRequestDict,
)
from tests.utils.helper import get_warning_logs, unit_test


@fixture
def username() -> str:
    """Username."""
    return "someUsername"


@fixture
def auth_domain() -> str:
    """Authentication domain as fixture."""
    return "some.auth.domain.com"


@fixture
def client_id() -> str:
    """Auth token client ID fixture."""
    return "oljorknkjnio"


@fixture
def scopes() -> str:
    """Auth token scopes fixture."""
    return "spaced out list of scopes"


@fixture
def audience() -> str:
    """Auth token audience fixture."""
    return "some.api.domain.com"


@fixture
def user_storage_path(tmp_path: Path, username: str) -> Path:
    """Temporary directory to act as user's .bitfount directory."""
    user_storage_path = tmp_path / username
    user_storage_path.mkdir()
    return user_storage_path


@fixture
def token_file(user_storage_path: Path) -> Path:
    """Path to save/load tokens from."""
    return user_storage_path / ".token"


@fixture
def bitfount_session(
    audience: str,
    auth_domain: str,
    client_id: str,
    scopes: str,
    user_storage_path: Path,
) -> BitfountSession:
    """Bitfount session instance as fixture."""
    return BitfountSession(auth_domain, client_id, user_storage_path, scopes, audience)


@fixture
def mock_webbrowser(mocker: MockerFixture) -> Mock:
    """Mock webbrowser import."""
    mock_webbrowser: Mock = mocker.patch(
        "bitfount.hub.authentication_flow.webbrowser", autospec=True
    )
    return mock_webbrowser


@fixture
def mock_time(mocker: MockerFixture) -> Mock:
    """Mock time import."""
    mock_time: Mock = mocker.patch(
        "bitfount.hub.authentication_flow.time", autospec=True
    )
    return mock_time


@fixture
def mock_datetime(mocker: MockerFixture) -> Mock:
    """Mock datetime import."""
    mock_datetime: Mock = mocker.patch(
        "bitfount.hub.authentication_flow.datetime", autospec=True
    )
    return mock_datetime


@unit_test
class TestBitfountSession:
    """Tests for the custom BitfountSession."""

    @fixture
    def device_code_request(
        self, audience: str, client_id: str, scopes: str
    ) -> _DeviceCodeRequestDict:
        """Expected request data for /oauth/device/code."""
        return {"audience": audience, "scope": scopes, "client_id": client_id}

    @fixture
    def device_code_response(self) -> _DeviceCodeResponseJSON:
        """Expected response from /oauth/device/code."""
        return {
            "device_code": "Ag_EE...ko1p",
            "user_code": "QTZL-MCBW",
            "verification_uri": "https://accounts.acmetest.org/activate",
            "verification_uri_complete": "https://accounts.acmetest.org"
            "/activate?user_code=QTZL-MCBW",
            "expires_in": 900,
            "interval": 5,
        }

    @fixture
    def device_code(self) -> str:
        """Device code."""
        return "someDeviceCode"

    @fixture
    def access_token(self) -> str:
        """Access token."""
        return "someAccessToken"

    @fixture
    def token_request(
        self, client_id: str, device_code: str
    ) -> _DeviceAccessTokenRequestDict:
        """Expected request data for /oauth/token."""
        return {
            "client_id": client_id,
            "grant_type": _DEVICE_CODE_GRANT_TYPE,
            "device_code": device_code,
        }

    @fixture
    def token_response(self) -> _DeviceAccessTokenResponseJSON:
        """Expected response data from /oauth/token."""
        return {
            "access_token": "eyJz93a...k4laUWw",
            "id_token": "eyJ...0NE",
            "refresh_token": "eyJ...MoQ",
            "scope": "...",
            "expires_in": 86400,
            "token_type": "Bearer",
        }

    @fixture
    def refresh_token(self) -> str:
        """Refresh token."""
        return "someRefreshToken"

    @fixture
    def token_refresh_request(
        self, client_id: str, refresh_token: str
    ) -> _TokenRefreshRequestDict:
        """Expected request data for refresh request to /oauth/token."""
        return {
            "client_id": client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

    @fixture
    def id_token_for_username(self, username: str) -> str:
        """The JWT ID token for username."""
        return jwt.encode({_USERNAME_KEY: username}, "Secret key", algorithm="HS256")

    def test_token_file_path(
        self,
        audience: str,
        auth_domain: str,
        client_id: str,
        scopes: str,
        tmp_path: Path,
    ) -> None:
        """Tests that token file is in provided path."""
        test_path = tmp_path / ".bitfount-unit-test" / "testToken"
        hs = BitfountSession(auth_domain, client_id, test_path, scopes, audience)
        # Token file is the path provided with the token file specified
        assert hs.token_file == test_path / ".token"

    @responses.activate
    def test_fetch_device_code_stores_and_returns_required_values(
        self,
        auth_domain: str,
        bitfount_session: BitfountSession,
        device_code_request: _DeviceCodeRequestDict,
        device_code_response: _DeviceCodeResponseJSON,
    ) -> None:
        """Checks that the needed attributes are stored from device code."""
        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/device/code",
            json=device_code_response,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], device_code_request)
                )
            ],
        )

        user_code, verification_uri = bitfount_session._fetch_device_code()

        assert bitfount_session.device_code == device_code_response.get("device_code")
        assert bitfount_session.device_code_arrival_time is not None
        assert bitfount_session.device_code_expires_in == device_code_response.get(
            "expires_in"
        )
        assert bitfount_session.token_request_interval == device_code_response.get(
            "interval"
        )
        assert user_code == device_code_response["user_code"]
        assert verification_uri == device_code_response["verification_uri_complete"]

    def test_do_verification_opens_browser_correctly(
        self,
        bitfount_session: BitfountSession,
        mock_webbrowser: Mock,
    ) -> None:
        """Checks that request to open browser works."""
        bitfount_session._do_verification("hello", "world")
        mock_webbrowser.open.assert_called_once_with("world")

    @responses.activate
    def test_exchange_device_code_for_token_eventually_receives_tokens(
        self,
        auth_domain: str,
        bitfount_session: BitfountSession,
        device_code: str,
        mock_time: Mock,
        token_request: _DeviceAccessTokenRequestDict,
        token_response: _DeviceAccessTokenResponseJSON,
    ) -> None:
        """Checks that device code successfully exchanged for token."""
        bitfount_session.device_code = device_code
        bitfount_session.device_code_arrival_time = datetime.now(timezone.utc)
        bitfount_session.device_code_expires_in = 2
        bitfount_session.token_request_interval = 1

        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            json={"error": _AUTHORIZATION_PENDING_ERROR},
            status=400,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_request)
                )
            ],
        )
        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            json=token_response,
            status=200,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_request)
                )
            ],
        )

        bitfount_session._exchange_device_code_for_token()

        assert len(responses.calls) == 2
        assert bitfount_session._access_token == token_response["access_token"]
        assert bitfount_session.refresh_token == token_response["refresh_token"]
        assert bitfount_session.id_token == token_response["id_token"]

        assert bitfount_session.access_token_expires_at is not None
        assert bitfount_session.access_token_expires_at > datetime.now(timezone.utc)
        mock_time.sleep.assert_called_once_with(1)

    @responses.activate
    def test_exchange_device_code_for_token_eventually_receives_error(
        self,
        auth_domain: str,
        bitfount_session: BitfountSession,
        device_code: str,
        mock_time: Mock,
        token_request: _DeviceAccessTokenRequestDict,
    ) -> None:
        """The token endpoint here eventually informs us that the user denied access."""
        bitfount_session.device_code = device_code
        bitfount_session.device_code_arrival_time = datetime.now(timezone.utc)
        bitfount_session.device_code_expires_in = 2
        bitfount_session.token_request_interval = 1

        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            json={"error": _AUTHORIZATION_PENDING_ERROR},
            status=400,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_request)
                )
            ],
        )
        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            json={"error": "access_denied"},
            status=400,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_request)
                )
            ],
        )

        with raises(ConnectionError):
            bitfount_session._exchange_device_code_for_token()

        assert len(responses.calls) == 2
        assert bitfount_session.access_token is None
        assert bitfount_session.refresh_token is None
        assert bitfount_session.id_token is None
        assert bitfount_session.access_token_expires_at is None
        assert all(map(lambda x: x == call(1), mock_time.sleep.call_args_list))

    @responses.activate
    def test_exchange_device_code_for_token_never_receives_tokens(
        self,
        auth_domain: str,
        bitfount_session: BitfountSession,
        device_code: str,
        mock_datetime: Mock,
        mock_time: Mock,
        token_request: _DeviceAccessTokenRequestDict,
    ) -> None:
        """The token endpoint here never issues tokens, so the device code expires."""
        bitfount_session.device_code = device_code
        bitfount_session.device_code_arrival_time = datetime(
            2020, 1, 14, tzinfo=timezone.utc
        )
        bitfount_session.device_code_expires_in = 300
        bitfount_session.token_request_interval = 1

        mock_datetime.now.side_effect = [
            datetime(2020, 1, 14, minute=x, tzinfo=timezone.utc)
            for x in range(0, 60, 2)
        ]

        auth_server_response = {"error": _AUTHORIZATION_PENDING_ERROR}

        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            json=auth_server_response,
            status=400,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_request)
                )
            ],
        )

        with raises(ConnectionError):
            bitfount_session._exchange_device_code_for_token()

        assert len(responses.calls) == 3

        assert all(map(lambda x: x == call(1), mock_time.sleep.call_args_list))
        assert len(mock_time.sleep.call_args_list) == 3

        assert bitfount_session.access_token is None
        assert bitfount_session.refresh_token is None
        assert bitfount_session.id_token is None
        assert bitfount_session.access_token_expires_at is None

    @responses.activate
    def test_exchange_device_code_for_token_receives_slow_down(
        self,
        auth_domain: str,
        bitfount_session: BitfountSession,
        caplog: LogCaptureFixture,
        capsys: CaptureFixture,
        device_code: str,
        mock_time: Mock,
        token_request: _DeviceAccessTokenRequestDict,
        token_response: _DeviceAccessTokenResponseJSON,
    ) -> None:
        """Test interval increased if receive slow down response."""
        # Set relevant attributes on session
        bitfount_session.device_code = device_code
        bitfount_session.device_code_arrival_time = datetime.now(timezone.utc)
        bitfount_session.device_code_expires_in = 300
        bitfount_session.token_request_interval = 1

        # First and second responses are "slow down"
        for _ in range(2):
            responses.add(
                responses.POST,
                f"https://{auth_domain}/oauth/token",
                json={"error": _SLOW_DOWN_ERROR},
                status=400,
                match=[
                    responses.matchers.urlencoded_params_matcher(
                        cast(Dict[str, str], token_request)
                    )
                ],
            )
        # Final response is correct response
        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            json=token_response,
            status=200,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_request)
                )
            ],
        )

        bitfount_session._exchange_device_code_for_token()

        # Check warning logs for interval notes
        warning_logs = get_warning_logs(caplog)
        assert (
            "Polling too quickly; increasing interval from 1 to 2 seconds"
            in warning_logs
        )
        assert (
            "Polling too quickly; increasing interval from 2 to 3 seconds"
            in warning_logs
        )
        # Check stdout for increased interval waits
        stdout = capsys.readouterr().out
        assert (
            "Awaiting authentication in browser. Will check again in 1 seconds."
            not in stdout
        )
        assert (
            "Awaiting authentication in browser. Will check again in 2 seconds."
            in stdout
        )
        assert (
            "Awaiting authentication in browser. Will check again in 3 seconds."
            in stdout
        )

        # Check correct number of requests made
        assert len(responses.calls) == 3

        # Check sleep called with updated intervals
        assert mock_time.sleep.call_args_list == [call(2), call(3)]

    @pytest.mark.parametrize(
        argnames=("content_type", "content_value", "expected_error_msg", "in_stdout"),
        argvalues=(
            pytest.param(
                "json",
                {},
                'An unexpected error occurred: status code: 404; "{}"',
                True,
                id="incorrect json",
            ),
            pytest.param(
                "body",
                "error but not necessarily json",
                (
                    "Received 404 status response, but JSON is invalid: "
                    '"error but not necessarily json"'
                ),
                False,
                id="non-json response",
            ),
        ),
    )
    @responses.activate
    def test_exchange_device_code_for_token_receives_non_400_error(
        self,
        auth_domain: str,
        bitfount_session: BitfountSession,
        caplog: LogCaptureFixture,
        capsys: CaptureFixture,
        content_type: Literal["json", "body"],
        content_value: Union[dict, str],
        device_code: str,
        expected_error_msg: str,
        in_stdout: bool,
        mock_time: Mock,
        remove_web_retry_backoff_sleep: Optional[Mock],
        token_request: _DeviceAccessTokenRequestDict,
        token_response: _DeviceAccessTokenResponseJSON,
    ) -> None:
        """Test error raised if receive non-400 error response."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        # Set relevant attributes on session
        bitfount_session.device_code = device_code
        bitfount_session.device_code_arrival_time = datetime.now(timezone.utc)
        bitfount_session.device_code_expires_in = 300
        bitfount_session.token_request_interval = 1

        partial_response_add = functools.partial(
            responses.add,
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            status=404,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_request)
                )
            ],
        )
        if content_type == "json":
            partial_response_add(json=content_value)
        else:
            partial_response_add(body=content_value)

        with pytest.raises(
            ConnectionError,
            match="Failed to retrieve a device code from the authentication server",
        ):
            bitfount_session._exchange_device_code_for_token()

        # Check logger/stdout for errors
        assert expected_error_msg in caplog.text
        if in_stdout:
            assert expected_error_msg in capsys.readouterr().out

        # Check retries occurred
        assert (
            remove_web_retry_backoff_sleep.call_count == web_utils._DEFAULT_MAX_RETRIES
        )

    @responses.activate
    def test_bitfount_session_request_provides_token(
        self,
        access_token: str,
        auth_domain: str,
        bitfount_session: BitfountSession,
        device_code: str,
    ) -> None:
        """Checks that `request()` call provides token."""
        bitfount_session._access_token = access_token
        bitfount_session.device_code = device_code
        # Expires 1 month in future
        bitfount_session.access_token_expires_at = datetime.now(
            timezone.utc
        ) + relativedelta(months=1)

        api_url = "https://some.api.url/goes/here"

        responses.add(
            responses.POST,
            api_url,
        )

        # Send request
        bitfount_session.request("POST", api_url)

        # Check request had access token
        assert (
            responses.calls[0].request.headers["authorization"]
            == f"Bearer {access_token}"
        )

    @responses.activate
    def test_bitfount_session_request_refreshes_expired_then_provides_token(
        self,
        access_token: str,
        auth_domain: str,
        bitfount_session: BitfountSession,
        device_code: str,
        id_token_for_username: str,
        mock_time: Mock,
        refresh_token: str,
        token_file: Path,
        token_refresh_request: _TokenRefreshRequestDict,
        token_response: _DeviceAccessTokenResponseJSON,
    ) -> None:
        """Checks that if token expired new one is provided and saved."""
        bitfount_session._access_token = access_token
        bitfount_session.device_code = device_code
        bitfount_session.refresh_token = refresh_token
        bitfount_session.id_token = id_token_for_username

        # Expire token
        bitfount_session.access_token_expires_at = datetime(
            2000, 1, 14, tzinfo=timezone.utc
        )
        bitfount_session.token_request_interval = 1

        api_url = "https://some.api.url/goes/here"

        # Set expected ID Token on response
        token_response["id_token"] = id_token_for_username

        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            # Token refresh has same form as initial token response so we just reuse it
            json=token_response,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_refresh_request)
                )
            ],
        )

        responses.add(
            responses.POST,
            api_url,
        )

        # Send request
        bitfount_session.request("POST", api_url)

        # Check request had refreshed access token
        assert (
            responses.calls[1].request.headers["authorization"]
            == f"Bearer {token_response['access_token']}"
        )

        # Check refreshed token was saved
        saved_token = json.load(token_file.open())
        assert saved_token["access_token"] == token_response["access_token"]
        assert saved_token["refresh_token"] == token_response["refresh_token"]
        assert saved_token["id_token"] == token_response["id_token"]
        assert datetime.fromtimestamp(
            saved_token["access_token_expires_at"], tz=timezone.utc
        ) > datetime.now(timezone.utc)

        # Check session metadata was saved
        assert saved_token["auth_domain"] == bitfount_session.auth_domain
        assert saved_token["client_id"] == bitfount_session.client_id
        assert saved_token["scopes"] == bitfount_session.scopes
        assert saved_token["audience"] == bitfount_session.audience

        mock_time.sleep.assert_not_called()

    @responses.activate
    def test_bitfount_session_request_forces_manual_login_when_refresh_fails(
        self,
        access_token: str,
        audience: str,
        auth_domain: str,
        bitfount_session: BitfountSession,
        client_id: str,
        device_code: str,
        device_code_request: _DeviceCodeRequestDict,
        device_code_response: _DeviceCodeResponseJSON,
        id_token_for_username: str,
        mock_time: Mock,
        mock_webbrowser: Mock,
        refresh_token: str,
        scopes: str,
        token_refresh_request: _TokenRefreshRequestDict,
        token_request: _DeviceAccessTokenRequestDict,
        token_response: _DeviceAccessTokenResponseJSON,
    ) -> None:
        """Checks that the user is made to log in if the token refresh fails.

        Once they have logged in the web request is completed
        """
        bitfount_session._access_token = access_token
        bitfount_session.device_code = device_code
        bitfount_session.refresh_token = refresh_token
        bitfount_session.id_token = id_token_for_username

        # Expire token
        bitfount_session.access_token_expires_at = datetime(
            2000, 1, 14, tzinfo=timezone.utc
        )
        bitfount_session.token_request_interval = 1

        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            json={"error": "some error"},
            status=401,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_refresh_request)
                )
            ],
        )

        # Set new device code on /oauth/device/code response and expected request
        # against /oauth/token
        new_device_code = "newDeviceCode"
        device_code_response["device_code"] = new_device_code
        token_request["device_code"] = new_device_code

        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/device/code",
            json=device_code_response,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], device_code_request)
                )
            ],
        )

        # Set ID Token on token response
        token_response["id_token"] = id_token_for_username

        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            json=token_response,
            status=200,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_request)
                )
            ],
        )

        expected_json = {"request": "success"}
        api_url = "https://some.api.url/goes/here"
        responses.add(responses.POST, api_url, json=expected_json)

        # Send request
        response = bitfount_session.request("POST", api_url)

        assert response.json() == expected_json
        mock_time.sleep.assert_called_once()
        mock_webbrowser.open.assert_called_once()

    def test_bitfount_session_authenticates_when_no_token_loaded(
        self,
        bitfount_session: BitfountSession,
        mocker: MockerFixture,
        username: str,
    ) -> None:
        """Checks that token requested and saved when none exists to load."""
        mock_fetch_device_code = mocker.patch.object(
            bitfount_session, "_fetch_device_code", return_value=(1, 2)
        )
        mock_do_verification = mocker.patch.object(bitfount_session, "_do_verification")
        mock_exchange_device_code = mocker.patch.object(
            bitfount_session, "_exchange_device_code_for_token"
        )
        mock_save_token = mocker.patch.object(bitfount_session, "_save_token_to_file")
        mocker.patch.object(
            bitfount_session, "_get_username_from_id_token", return_value=username
        )

        bitfount_session.authenticate()

        mock_fetch_device_code.assert_called_once()
        mock_do_verification.assert_called_once_with(1, 2)
        mock_exchange_device_code.assert_called_once()
        mock_save_token.assert_called_once_with(bitfount_session.token_file)

    def test_bitfount_session_authenticates_when_token_loaded_but_expired(
        self,
        access_token: str,
        bitfount_session: BitfountSession,
        id_token_for_username: str,
        mocker: MockerFixture,
        refresh_token: str,
        token_file: Path,
    ) -> None:
        """Checks that a new token is fetched via the login flow.

        This is the case where the loaded token has expired completely.
        """
        # Create saved token
        bitfount_session._access_token = access_token
        bitfount_session.access_token_expires_at = datetime(
            year=2000, month=6, day=13, tzinfo=timezone.utc
        )
        bitfount_session.id_token = id_token_for_username
        bitfount_session.refresh_token = refresh_token
        bitfount_session._save_token_to_file(token_file)

        # Reset session to initial state
        bitfount_session._access_token = None
        bitfount_session.access_token_expires_at = None
        bitfount_session.id_token = None
        bitfount_session.refresh_token = None

        mocker.patch.object(
            bitfount_session, "_refresh_access_token", return_value=False
        )
        mock_fetch_device_code = mocker.patch.object(
            bitfount_session, "_fetch_device_code", return_value=(1, 2)
        )
        mock_do_verification = mocker.patch.object(bitfount_session, "_do_verification")
        mock_exchange_device_code = mocker.patch.object(
            bitfount_session, "_exchange_device_code_for_token"
        )

        bitfount_session.authenticate()

        mock_fetch_device_code.assert_called_once()
        mock_do_verification.assert_called_once_with(1, 2)
        mock_exchange_device_code.assert_called_once()

    def test_bitfount_session_refreshes_when_token_loaded_but_expired(
        self,
        access_token: str,
        bitfount_session: BitfountSession,
        id_token_for_username: str,
        mocker: MockerFixture,
        refresh_token: str,
        token_file: Path,
    ) -> None:
        """Checks that a new token is fetched using the refresh mechanism.

        This is for when the loaded token has expired,
        but the refresh token is still valid
        """
        # Create saved token
        bitfount_session._access_token = access_token
        bitfount_session.access_token_expires_at = datetime(
            year=2000, month=6, day=13, tzinfo=timezone.utc
        )
        bitfount_session.id_token = id_token_for_username
        bitfount_session.refresh_token = refresh_token
        bitfount_session._save_token_to_file(token_file)

        # Reset session to initial state
        bitfount_session._access_token = None
        bitfount_session.access_token_expires_at = None
        bitfount_session.id_token = None
        bitfount_session.refresh_token = None

        mock_refresh_access_token = mocker.patch.object(
            bitfount_session, "_refresh_access_token"
        )
        mock_fetch_device_code = mocker.patch.object(
            bitfount_session, "_fetch_device_code"
        )
        mock_do_verification = mocker.patch.object(bitfount_session, "_do_verification")
        mock_exchange_device_code = mocker.patch.object(
            bitfount_session, "_exchange_device_code_for_token"
        )

        bitfount_session.authenticate()

        # Ensure refresh was called
        mock_refresh_access_token.assert_called_once()
        # Ensure manual login flow is not run
        mock_fetch_device_code.assert_not_called()
        mock_do_verification.assert_not_called()
        mock_exchange_device_code.assert_not_called()

    def test_bitfount_session_authenticated_when_valid_token_loaded(
        self,
        access_token: str,
        bitfount_session: BitfountSession,
        id_token_for_username: str,
        mocker: MockerFixture,
        refresh_token: str,
        token_file: Path,
    ) -> None:
        """Checks that authentication is successful when token loaded from file."""
        # Create saved token
        bitfount_session._access_token = access_token
        # Timestamp for 1 month from now
        bitfount_session.access_token_expires_at = datetime.now(
            timezone.utc
        ) + relativedelta(months=1)
        bitfount_session.id_token = id_token_for_username
        bitfount_session.refresh_token = refresh_token
        bitfount_session._save_token_to_file(token_file)

        # Reset session to initial state
        bitfount_session._access_token = None
        bitfount_session.access_token_expires_at = None
        bitfount_session.id_token = None
        bitfount_session.refresh_token = None

        mock_fetch_device_code = mocker.patch.object(
            bitfount_session, "_fetch_device_code"
        )
        mock_exchange_device_code = mocker.patch.object(
            bitfount_session, "_exchange_device_code_for_token"
        )

        bitfount_session.authenticate()

        mock_fetch_device_code.assert_not_called()
        mock_exchange_device_code.assert_not_called()

    def test_bitfount_session_doesnt_use_loaded_token_when_metadata_differs(
        self,
        access_token: str,
        bitfount_session: BitfountSession,
        id_token_for_username: str,
        mocker: MockerFixture,
        refresh_token: str,
        token_file: Path,
        user_storage_path: Path,
    ) -> None:
        """Test bitfount session will create & save a new token when different."""
        # Create saved token
        old_session_configuration = BitfountSession(
            "someOtherDomain.com",
            "not our client id",
            user_storage_path,
            "not our scopes",
            "someOtherAudience",
        )
        old_session_configuration._access_token = access_token
        # Timestamp for 1 month from now
        old_session_configuration.access_token_expires_at = datetime.now(
            timezone.utc
        ) + relativedelta(months=1)
        bitfount_session.id_token = id_token_for_username
        old_session_configuration.refresh_token = refresh_token
        old_session_configuration._save_token_to_file(token_file)

        mock_fetch_device_code = mocker.patch.object(
            bitfount_session, "_fetch_device_code", return_value=(1, 2)
        )
        mock_do_verification = mocker.patch.object(bitfount_session, "_do_verification")
        mock_exchange_device_code = mocker.patch.object(
            bitfount_session, "_exchange_device_code_for_token"
        )
        mock_save_token = mocker.patch.object(bitfount_session, "_save_token_to_file")

        bitfount_session.authenticate()

        mock_fetch_device_code.assert_called_once()
        mock_do_verification.assert_called_once_with(1, 2)
        mock_exchange_device_code.assert_called_once()
        mock_save_token.assert_called_once_with(token_file)

    @responses.activate
    def test_send_token_request_to_refresh_expired_token(
        self,
        auth_domain: str,
        bitfount_session: BitfountSession,
        refresh_token: str,
        token_refresh_request: _TokenRefreshRequestDict,
    ) -> None:
        """Checks _send_token_request works with refresh=True."""
        bitfount_session.refresh_token = refresh_token

        auth_server_response = {"some": "response"}

        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            json=auth_server_response,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_refresh_request)
                )
            ],
        )

        response = bitfount_session._send_token_request(refresh=True)

        assert response.json() == auth_server_response

    @responses.activate
    def test_send_token_request_as_device_code(
        self,
        auth_domain: str,
        bitfount_session: BitfountSession,
        client_id: str,
        device_code: str,
        token_request: _DeviceAccessTokenRequestDict,
    ) -> None:
        """Checks that _send_token_request works correctly."""
        bitfount_session.device_code = device_code

        auth_server_response = {"some": "response"}

        responses.add(
            responses.POST,
            f"https://{auth_domain}/oauth/token",
            json=auth_server_response,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], token_request)
                )
            ],
        )

        response = bitfount_session._send_token_request()

        assert response.json() == auth_server_response

    def test_get_username_from_id_token(
        self,
        bitfount_session: BitfountSession,
        id_token_for_username: str,
        username: str,
    ) -> None:
        """Tests username can be extracted from ID Token."""
        bitfount_session.id_token = id_token_for_username

        assert bitfount_session._get_username_from_id_token() == username

    @pytest.mark.parametrize(
        "_username, assertion_error",
        [(lazy_fixture("username"), False), ("not-real-username", True)],
    )
    def test_verify_user_storage_path(
        self,
        _username: str,
        assertion_error: bool,
        bitfount_session: BitfountSession,
        mocker: MockerFixture,
    ) -> None:
        """Tests that token won't be saved in a directory with a different username."""
        mocker.patch.object(
            bitfount_session, "_get_username_from_id_token", return_value=_username
        )

        if assertion_error:
            with pytest.raises(AssertionError):
                bitfount_session._verify_user_storage_path()
        else:
            bitfount_session._verify_user_storage_path()


@unit_test
@pytest.mark.parametrize(
    argnames=(
        "environment",
        "expected_name",
        "expected_auth_domain",
        "expected_client_id",
    ),
    argvalues=(
        pytest.param(
            _STAGING_ENVIRONMENT,
            "staging",
            _STAGING_AUTH_DOMAIN,
            _STAGING_CLIENT_ID,
            id="staging",
        ),
        pytest.param(
            _DEVELOPMENT_ENVIRONMENT,
            "development",
            _DEVELOPMENT_AUTH_DOMAIN,
            _DEVELOPMENT_CLIENT_ID,
            id="development",
        ),
        pytest.param(
            _PRODUCTION_ENVIRONMENT,
            "production",
            _PRODUCTION_AUTH_DOMAIN,
            _PRODUCTION_CLIENT_ID,
            id="production",
        ),
    ),
)
def test_get_auth_environment(
    environment: str,
    expected_auth_domain: str,
    expected_client_id: str,
    expected_name: str,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests _get_auth_environment with various envvar values."""
    # Patch out environment variable
    monkeypatch.setenv("BITFOUNT_ENVIRONMENT", environment)

    # Check return
    assert _get_auth_environment() == _AuthEnv(
        expected_name, expected_auth_domain, expected_client_id
    )
