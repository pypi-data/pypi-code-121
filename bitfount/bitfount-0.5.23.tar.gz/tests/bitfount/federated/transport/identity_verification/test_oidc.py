"""Tests for modeller-side OIDC handling."""
import asyncio
from asyncio import Task
import base64
from datetime import datetime, timedelta, timezone
import functools
import hashlib
import logging
import re
import secrets
from typing import Dict, List, Literal, Optional, Type, cast
from unittest.mock import Mock, call, create_autospec
from urllib.parse import urlencode

from _pytest.capture import CaptureFixture
from _pytest.logging import LogCaptureFixture
from aiohttp import web
from aiohttp.pytest_plugin import AiohttpClient
from aiohttp.test_utils import TestClient
from aiohttp.web import Application
from aiohttp.web_runner import TCPSite
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
from requests import HTTPError
from requests.exceptions import InvalidJSONError
import responses
from responses import matchers

from bitfount import web_utils
from bitfount.federated.transport.identity_verification import _BITFOUNT_MODELLER_PORT
from bitfount.federated.transport.identity_verification.oidc import (
    _CALLBACK_ROUTE,
    _get_urlsafe_hash,
    _OIDCAuthFlowChallengeHandler,
    _OIDCDeviceCodeHandler,
    _OIDCWebEndpoint,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.types import (
    _DeviceCodeDetailsPair,
    _ModellerDeviceCodeDetails,
    _OIDCAuthEndpointResponse,
    _OIDCAuthFlowResponse,
    _OIDCClientID,
    _PodDeviceCodeDetails,
)
from bitfount.hub.authentication_flow import AuthEnvironmentError, _AuthEnv
from bitfount.hub.types import _DeviceCodeRequestDict, _DeviceCodeResponseJSON
from tests.utils.helper import get_critical_logs, get_info_logs, unit_test
from tests.utils.mocks import AwaitableMock


@unit_test
class TestOIDCWebEndpoint:
    """Tests for the OIDC web endpoint."""

    @fixture
    def oidc_web_endpoint(self) -> _OIDCWebEndpoint:
        """A web endpoint for OIDC authentication."""
        return _OIDCWebEndpoint()

    @fixture
    def mock_webbrowser(self, mocker: MockerFixture) -> Mock:
        """Mock webbrowser import."""
        return mocker.patch(
            "bitfount.federated.transport.identity_verification.oidc.webbrowser",
            autospec=True,
        )

    @fixture
    def authorize_urls(self) -> List[str]:
        """List of URLs for authorize calls."""
        return ["first_url", "second_url", "third_url"]

    @fixture
    def pod_identifiers(self) -> List[str]:
        """Pod identifiers."""
        return ["user1/pod1", "user2/pod2", "user3/pod3"]

    @fixture
    def states(self, pod_identifiers: List[str]) -> Dict[str, str]:
        """Randomly generated states for API calls."""
        return {pod_id: secrets.token_hex(nbytes=32) for pod_id in pod_identifiers}

    @fixture
    def auth_codes(self) -> List[str]:
        """Fake auth codes as though generated from /authorize."""
        return [f"auth_code_{i}" for i in range(3)]

    @fixture
    def callback_urls(self, auth_codes: List[str], states: Dict[str, str]) -> List[str]:
        """Callback URLs as though generated from /authorize."""
        return [
            f'{_CALLBACK_ROUTE}?{urlencode({"code": auth_codes[i], "state": states[pod_id]})}'  # noqa: B950
            for i, pod_id in enumerate(states)
        ]

    @fixture
    async def client(
        self, aiohttp_client: AiohttpClient, oidc_web_endpoint: _OIDCWebEndpoint
    ) -> TestClient:
        """Test client for AioHTTP interactions."""
        app = Application()
        app.add_routes([web.get(_CALLBACK_ROUTE, oidc_web_endpoint.process_callback)])
        return await aiohttp_client(app)

    def test_start_processing(
        self,
        authorize_urls: List[str],
        caplog: LogCaptureFixture,
        mock_webbrowser: Mock,
        oidc_web_endpoint: _OIDCWebEndpoint,
        states: Dict[str, str],
    ) -> None:
        """Test start processing opens the initial url."""
        # Initialise endpoint
        oidc_web_endpoint.initialise(authorize_urls, states)

        with caplog.at_level(logging.INFO):
            oidc_web_endpoint.start_processing()

        # Check first URL opened
        mock_webbrowser.open.assert_called_once_with(authorize_urls[0])
        # Check logged out first URL
        info_logs = get_info_logs(caplog)
        assert (
            f"Attempting to open browser. Running a headless client? "
            f"You'll need to open this link in a browser: {authorize_urls[0]}"
            in info_logs
        )
        # Check first URL dropped from iterator
        assert list(oidc_web_endpoint._urls_iter) == authorize_urls[1:]

    def test_start_processing_throws_error_if_not_initialized(
        self,
        caplog: LogCaptureFixture,
        mock_webbrowser: Mock,
        oidc_web_endpoint: _OIDCWebEndpoint,
    ) -> None:
        """Test start processing throws exception if not initialised."""
        expected_log_message = (
            "OIDC callback endpoint has not been initialised. "
            "Unable to complete OIDC authentication."
        )

        with pytest.raises(RuntimeError, match=re.escape(expected_log_message)):
            oidc_web_endpoint.start_processing()

        # Check logged out error
        critical_logs = get_critical_logs(caplog)
        assert expected_log_message in critical_logs
        # Check webbrowser not opened
        mock_webbrowser.open.assert_not_called()

    def test_initialise_sets_initialised_variable(
        self,
        authorize_urls: List[str],
        oidc_web_endpoint: _OIDCWebEndpoint,
        states: Dict[str, str],
    ) -> None:
        """Tests that initialise() sets initialised variable."""
        assert oidc_web_endpoint._initialised is False
        oidc_web_endpoint.initialise(authorize_urls, states)
        assert oidc_web_endpoint._initialised is True

    async def test_process_callback_loop(
        self,
        auth_codes: List[str],
        authorize_urls: List[str],
        callback_urls: List[str],
        client: TestClient,
        mock_webbrowser: Mock,
        oidc_web_endpoint: _OIDCWebEndpoint,
        states: Dict[str, str],
    ) -> None:
        """Tests process_callback() successfully redirects to all authorizations."""
        oidc_web_endpoint.initialise(authorize_urls, states)

        # These requests would normally be made by the user's browser after being
        # redirected after making a /authorize API call (which happens in the
        # `start_processing()` call).
        oidc_web_endpoint.start_processing()
        # First OIDC authorize response (i.e. first callback URL)
        first_authorize_redirect = await client.get(
            callback_urls[0], allow_redirects=False
        )
        # First redirect takes us to the second /authorize URL as the first is
        # opened by the user.
        assert first_authorize_redirect.headers["location"] == authorize_urls[1]
        assert not oidc_web_endpoint.all_done.is_set()

        # Second OIDC authorize response (i.e. second callback URL)
        second_authorize_redirect = await client.get(
            callback_urls[1], allow_redirects=False
        )
        # Second redirect takes us to the third /authorize URL.
        assert second_authorize_redirect.headers["location"] == authorize_urls[2]
        assert not oidc_web_endpoint.all_done.is_set()

        # Third callback URL should take us to the success page
        success_page = await client.get(callback_urls[2], allow_redirects=False)
        assert str(success_page.url.path) == _CALLBACK_ROUTE
        page_text = await success_page.text()
        assert (
            page_text == "You've now proven your identity to all pods involved"
            " in the task. You can close this tab."
        )
        # Should be all done now (including empty URLs iterator)
        assert oidc_web_endpoint.all_done.is_set()
        with pytest.raises(StopIteration):
            next(oidc_web_endpoint._urls_iter)

        # Check states match
        assert oidc_web_endpoint._id_to_state == states
        # Check responses
        responses = oidc_web_endpoint._responses
        assert responses == {
            pod_id: _OIDCAuthEndpointResponse(
                auth_codes[i],
                states[pod_id],
            )
            for i, pod_id in enumerate(states)
        }

    async def test_process_callback_fails_if_not_initialized(
        self, caplog: LogCaptureFixture, oidc_web_endpoint: _OIDCWebEndpoint
    ) -> None:
        """Test process_callback() raises exception if not initialized."""
        expected_log_message = (
            "OIDC callback endpoint has not been initialised. "
            "Unable to complete OIDC authentication."
        )

        with pytest.raises(RuntimeError, match=re.escape(expected_log_message)):
            await oidc_web_endpoint.process_callback(request=Mock())

        # Check logged out error
        critical_logs = get_critical_logs(caplog)
        assert expected_log_message in critical_logs

    async def test_get_responses_waits_for_completion(
        self, mocker: MockerFixture, oidc_web_endpoint: _OIDCWebEndpoint
    ) -> None:
        """Tests that get_responses() waits for all_done to be set."""
        # Mock out responses
        mock_responses = mocker.patch.object(
            oidc_web_endpoint, "_responses", autospec=True
        )

        # Mock out all_done event
        mock_all_done = mocker.patch.object(
            oidc_web_endpoint, "all_done", autospec=True
        )

        responses = await oidc_web_endpoint.get_responses()

        # Check waited on all_done event
        mock_all_done.wait.assert_awaited_once()
        # Check returned correctly
        assert responses == mock_responses


@pytest.mark.parametrize(argnames="initial_encoding", argvalues=("utf-8", "ascii"))
@unit_test
def test__get_urlsafe_hash(initial_encoding: str) -> None:
    """Test _get_urlsafe_hash() produces expected hash."""
    test_string = "Hello, world!"

    # Create expected hash
    encoded_s: bytes = test_string.encode(initial_encoding)
    sha256_hash: bytes = hashlib.sha256(encoded_s).digest()
    b64_hash: bytes = base64.urlsafe_b64encode(sha256_hash)
    b64_hash_str: str = b64_hash.decode("utf-8").replace("=", "")

    assert _get_urlsafe_hash(test_string) == b64_hash_str


@fixture
def auth_domain() -> str:
    """Fake auth domain."""
    return "fake_auth_domain"


@fixture
def scopes() -> str:
    """Fake oauth scopes."""
    return "fake scopes for auth0"


@fixture
def audience() -> str:
    """Fake oauth audience."""
    return "fake_audience"


@fixture
def client_id() -> str:
    """Fake client ID."""
    return "fake_client_id"


@fixture
def fake_auth_env(auth_domain: str, client_id: str) -> _AuthEnv:
    """Fake _AuthEnv instance for tests."""
    return _AuthEnv(
        name="fake_auth_env",
        auth_domain=auth_domain,
        client_id=client_id,
    )


@fixture
def patch_get_auth_environment(fake_auth_env: _AuthEnv, mocker: MockerFixture) -> Mock:
    """Patch out the return value of _get_auth_environment() to our fake env."""
    mock_get_auth_environment = mocker.patch(
        "bitfount.federated.transport.identity_verification.oidc._get_auth_environment",  # noqa: B950
        autospec=True,
        return_value=fake_auth_env,
    )
    return mock_get_auth_environment


@fixture
def mock_modeller_mailbox() -> Mock:
    """Mock _ModellerMailbox instance."""
    mock_mailbox: Mock = create_autospec(_ModellerMailbox, instance=True)
    return mock_mailbox


@fixture
def num_pods() -> int:
    """The number of pods to replicate in handle tests."""
    return 3


@fixture
def pod_identifiers(num_pods: int) -> List[str]:
    """Pod identifiers."""
    return [f"user{i}/pod{i}" for i in range(num_pods)]


@fixture
def received_oidc_details(
    client_id: str, pod_identifiers: List[str]
) -> Dict[str, _OIDCClientID]:
    """Fake received OIDC details as would be received from pods."""
    return {pod_id: _OIDCClientID(client_id) for pod_id in pod_identifiers}


@unit_test
class TestOIDCAuthFlowChallengeHandler:
    """Tests for _OIDCAuthFlowChallengeHandler."""

    @fixture
    def oidc_auth_flow_handler(
        self, audience: str, auth_domain: str, scopes: str
    ) -> _OIDCAuthFlowChallengeHandler:
        """OIDC Authorisation Code Flow challenge handler."""
        return _OIDCAuthFlowChallengeHandler(auth_domain, scopes, audience)

    @fixture
    def code_verifiers(self, num_pods: int) -> List[str]:
        """Pregenerated code verifiers for /authorize requests."""
        return [secrets.token_urlsafe(nbytes=60) for _ in range(num_pods)]

    @fixture
    def code_challenges(self, code_verifiers: List[str]) -> List[str]:
        """Code challenges for the pregenerated code verifiers."""
        return [
            _get_urlsafe_hash(cv, initial_encoding="ascii") for cv in code_verifiers
        ]

    @fixture
    def states(self, num_pods: int) -> List[str]:
        """Pregenerated states for /authorize requests."""
        return [secrets.token_hex(nbytes=32) for _ in range(num_pods)]

    @fixture
    def states_dict(
        self, pod_identifiers: List[str], states: List[str]
    ) -> Dict[str, str]:
        """Dictionary of pod IDs to the pregenerated states."""
        return {pod_id: state for pod_id, state in zip(pod_identifiers, states)}

    @fixture
    def expected_authorize_urls(
        self,
        audience: str,
        client_id: str,
        code_challenges: List[str],
        num_pods: int,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
        scopes: str,
        states: List[str],
    ) -> List[str]:
        """Expected /authorize URLs (with pregenerated params)."""
        expected_params = [
            urlencode(
                {
                    "audience": audience,
                    "scope": scopes,
                    "response_type": "code",
                    "client_id": client_id,
                    "state": states[i],
                    "redirect_uri": oidc_auth_flow_handler._redirect_uri,
                    "code_challenge_method": "S256",
                    "code_challenge": code_challenges[i],
                }
            )
            for i in range(num_pods)
        ]
        return [
            f"{oidc_auth_flow_handler._authorize_endpoint}?{params}"
            for params in expected_params
        ]

    @fixture
    def auth_codes(self, num_pods: int) -> List[str]:
        """Fake auth codes to return from web endpoint."""
        return [f"auth_code_{i}" for i in range(num_pods)]

    @fixture
    def final_oidc_details(
        self,
        auth_codes: List[str],
        code_verifiers: List[str],
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
        pod_identifiers: List[str],
    ) -> Dict[str, _OIDCAuthFlowResponse]:
        """Final OIDC details to send back to pods."""
        return {
            pod_id: _OIDCAuthFlowResponse(
                auth_codes[i], code_verifiers[i], oidc_auth_flow_handler._redirect_uri
            )
            for i, pod_id in enumerate(pod_identifiers)
        }

    @fixture
    def fake_endpoint_responses(
        self, auth_codes: List[str], pod_identifiers: List[str], states: List[str]
    ) -> Dict[str, _OIDCAuthEndpointResponse]:
        """Fake _OIDCWebEndpoint.get_responses() return value."""
        return {
            pod_id: _OIDCAuthEndpointResponse(
                auth_codes[i],
                states[i],
            )
            for i, pod_id in enumerate(pod_identifiers)
        }

    async def test_start_server(
        self,
        mocker: MockerFixture,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
    ) -> None:
        """Test start() correctly starts the server."""
        # Mock out site start-up method and init
        mock_tcp_site = create_autospec(TCPSite)
        mock_tcp_site_init = mocker.patch(
            "bitfount.federated.transport.identity_verification.oidc.TCPSite",
            autospec=True,
            return_value=mock_tcp_site,
        )

        # Check server not marked as started
        with pytest.raises(AttributeError):
            oidc_auth_flow_handler._server_start_task

        server_start_task = oidc_auth_flow_handler.start_server()
        await server_start_task

        # Check server now marked as started
        assert oidc_auth_flow_handler._server_start_task.done()
        # Check TCP site created and started
        mock_tcp_site_init.assert_called_once_with(
            oidc_auth_flow_handler._runner, "localhost", _BITFOUNT_MODELLER_PORT
        )
        mock_tcp_site.start.assert_awaited_once()

    async def test__start_times_out_after_time(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
    ) -> None:
        """Tests that _start() will timeout if server start hangs."""
        # Mock out runner
        mock_runner = mocker.patch.object(
            oidc_auth_flow_handler, "_runner", autospec=True
        )

        # Mock out site start-up method and init
        mock_tcp_site = create_autospec(TCPSite)
        mock_tcp_site_init = mocker.patch(
            "bitfount.federated.transport.identity_verification.oidc.TCPSite",
            autospec=True,
            return_value=mock_tcp_site,
        )

        # Make wait_for raise timeout exception
        mocker.patch.object(
            asyncio, "wait_for", side_effect=TimeoutError("custom timeout")
        )

        with pytest.raises(TimeoutError, match="custom timeout"):
            await oidc_auth_flow_handler._start()

        # Check setup called and site created
        mock_runner.setup.assert_awaited_once()
        mock_tcp_site_init.assert_called_once()

        # Check logged exception
        critical_logs = get_critical_logs(caplog)
        assert (
            "Timeout reached whilst trying to bind OIDC web endpoint" in critical_logs
        )

    async def test__start_handles_address_in_use_error(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
    ) -> None:
        """Tests that _start() handles address being unavailable."""
        # Mock out runner
        mock_runner = mocker.patch.object(
            oidc_auth_flow_handler, "_runner", autospec=True
        )

        # Mock out site start-up method and init
        mock_tcp_site = create_autospec(TCPSite)
        mock_tcp_site_init = mocker.patch(
            "bitfount.federated.transport.identity_verification.oidc.TCPSite",
            autospec=True,
            return_value=mock_tcp_site,
        )
        # Make site.start() raise error indicating address unavailable
        mock_tcp_site.start.side_effect = OSError()

        with pytest.raises(OSError):
            await oidc_auth_flow_handler._start()

        # Check setup called and site created
        mock_runner.setup.assert_awaited_once()
        mock_tcp_site_init.assert_called_once()

        # Check logged exception
        critical_logs = get_critical_logs(caplog)
        assert "Unable to bind OIDC web endpoint" in critical_logs

    def test__verify_client_ids_successful(
        self,
        client_id: str,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
        patch_get_auth_environment: Mock,
    ) -> None:
        """Test _verify_client_ids() passes correctly."""
        oidc_details = {f"user{i}/pod{i}": _OIDCClientID(client_id) for i in range(3)}

        # Should just pass happily
        oidc_auth_flow_handler._verify_client_ids(oidc_details)

    def test__verify_client_ids_fails_diff_auth_domain(
        self,
        auth_domain: str,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
        patch_get_auth_environment: Mock,
    ) -> None:
        """Test _verify_client_ids() fails if auth domains differ."""
        # Change _auth_domain on the handler to induce mismatch
        oidc_auth_flow_handler._auth_domain = "not_the_same"

        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Mismatch between setup auth environment and current: "
                f"expected {oidc_auth_flow_handler._auth_domain}, got {auth_domain}"
            ),
        ):
            oidc_auth_flow_handler._verify_client_ids({})

    def test__verify_client_ids_fails_diff_client_ids(
        self,
        client_id: str,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
        patch_get_auth_environment: Mock,
    ) -> None:
        """Test _verify_client_ids() fails if client IDs differ."""
        # Have one "correct" client_id
        oidc_details = {
            "user0/pod0": _OIDCClientID(client_id),
        }
        # Add two "incorrect" client_ids
        incorrect_oidc_details = {
            f"user{i}/pod{i}": _OIDCClientID(f"diff_client_id_{i}") for i in range(1, 3)
        }
        oidc_details.update(incorrect_oidc_details)

        # Create expected error message
        error_pods = "; ".join(
            [
                f"Pod ID = {pod_id}, Client ID = {details.client_id}"
                for pod_id, details in incorrect_oidc_details.items()
            ]
        )
        expected_error_message = (
            f"Authorisation environments do not match. Expected client_id "
            f'"{client_id}" but the following pods mismatched: {error_pods}'
        )

        with pytest.raises(
            AuthEnvironmentError, match=re.escape(expected_error_message)
        ):
            oidc_auth_flow_handler._verify_client_ids(oidc_details)

    async def test_handle(
        self,
        caplog: LogCaptureFixture,
        code_verifiers: List[str],
        expected_authorize_urls: List[str],
        fake_endpoint_responses: Dict[str, _OIDCAuthEndpointResponse],
        final_oidc_details: Dict[str, _OIDCAuthFlowResponse],
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
        patch_get_auth_environment: Mock,
        received_oidc_details: Dict[str, _OIDCClientID],
        states: List[str],
        states_dict: Dict[str, str],
    ) -> None:
        """Tests handle() correctly processes OIDC challenges."""
        # Mock out receiving of OIDC details
        mock_modeller_mailbox.get_oidc_client_ids.return_value = received_oidc_details

        # Mock out code_verifier generation
        mock_secrets = mocker.patch(
            "bitfount.federated.transport.identity_verification.oidc.secrets",
            autospec=True,
        )
        mock_secrets.token_urlsafe.side_effect = code_verifiers

        # Mock out state generation
        mock_secrets.token_hex.side_effect = states

        # Mock out runner and web endpoint
        mock_runner = mocker.patch.object(
            oidc_auth_flow_handler, "_runner", autospec=True
        )
        mock_endpoint = mocker.patch.object(
            oidc_auth_flow_handler, "_oidc_endpoint", autospec=True
        )
        mock_endpoint.get_responses.return_value = fake_endpoint_responses

        # Mock out server_start_task
        mock_server_start_task = AwaitableMock(spec=Task)
        mock_server_start_task.done.return_value = False
        oidc_auth_flow_handler._server_start_task = mock_server_start_task

        # Make call
        with caplog.at_level(logging.INFO):
            await oidc_auth_flow_handler.handle(mock_modeller_mailbox)

        # Check logs
        info_logs = get_info_logs(caplog)
        assert "Waiting for OIDC challenge handler to start" in info_logs

        # Check endpoint interactions
        mock_endpoint.initialise.assert_called_once_with(
            expected_authorize_urls,
            states_dict,
        )
        mock_endpoint.start_processing.assert_called_once()

        # Check server_start_task and runner interactions
        mock_server_start_task.done.assert_called_once()
        mock_server_start_task.assert_awaited_once()
        mock_server_start_task.result.assert_called_once()

        # Check correct details sent onwards
        mock_modeller_mailbox.send_oidc_auth_flow_responses.assert_awaited_once_with(
            final_oidc_details
        )

        # Check server is shutdown
        mock_runner.cleanup.assert_awaited()

    async def test_handle_fails_different_states(
        self,
        caplog: LogCaptureFixture,
        code_verifiers: List[str],
        expected_authorize_urls: List[str],
        fake_endpoint_responses: Dict[str, _OIDCAuthEndpointResponse],
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
        patch_get_auth_environment: Mock,
        pod_identifiers: List[str],
        received_oidc_details: Dict[str, _OIDCClientID],
        states: List[str],
        states_dict: Dict[str, str],
    ) -> None:
        """Tests handle() fails if sent states and received states mismatch."""
        # Mock out receiving of OIDC details
        mock_modeller_mailbox.get_oidc_client_ids.return_value = received_oidc_details

        # Mock out code_verifier generation
        mock_secrets = mocker.patch(
            "bitfount.federated.transport.identity_verification.oidc.secrets",
            autospec=True,
        )
        mock_secrets.token_urlsafe.side_effect = code_verifiers

        # Mock out state generation
        mock_secrets.token_hex.side_effect = states

        # Mock out runner and web endpoint
        mock_runner = mocker.patch.object(
            oidc_auth_flow_handler, "_runner", autospec=True
        )
        mock_endpoint = mocker.patch.object(
            oidc_auth_flow_handler, "_oidc_endpoint", autospec=True
        )
        # Modify states to make not match on one
        fake_endpoint_responses[pod_identifiers[-1]].state = "incorrect_state"
        mock_endpoint.get_responses.return_value = fake_endpoint_responses

        mock_server_start_task = AwaitableMock(spec=Task)
        mock_server_start_task.done.return_value = True
        oidc_auth_flow_handler._server_start_task = mock_server_start_task

        # Make call
        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Unable to validate response intended for {pod_identifiers[-1]}"
            ),
        ), caplog.at_level(logging.INFO):
            await oidc_auth_flow_handler.handle(mock_modeller_mailbox)

        # Check log DIDN'T wait
        info_logs = get_info_logs(caplog)
        assert "Waiting for OIDC challenge handler to start" not in info_logs

        # Check endpoint interactions
        mock_endpoint.initialise.assert_called_once_with(
            expected_authorize_urls,
            states_dict,
        )
        mock_endpoint.start_processing.assert_called_once()

        # Check server_start_task and runner interactions
        mock_server_start_task.done.assert_called_once()
        mock_server_start_task.result.assert_called_once()
        mock_server_start_task.assert_not_awaited()
        # Check server is still shutdown
        mock_runner.cleanup.assert_awaited()

    async def test_handle_fails_if_server_not_started(
        self,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
    ) -> None:
        """Tests handle() fails if server not started."""
        # Mock out runner
        mock_runner = mocker.patch.object(
            oidc_auth_flow_handler, "_runner", autospec=True
        )

        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "OIDC server has not been started; "
                "ensure start_server() has been called."
            ),
        ):
            await oidc_auth_flow_handler.handle(mock_modeller_mailbox)

        # Check server is still shutdown
        mock_runner.cleanup.assert_awaited()

    @pytest.mark.parametrize(
        argnames="server_start_exception_cls",
        argvalues=(TimeoutError, OSError, Exception),
    )
    async def test_handle_reraises_exception_from_start_task(
        self,
        code_verifiers: List[str],
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        oidc_auth_flow_handler: _OIDCAuthFlowChallengeHandler,
        patch_get_auth_environment: Mock,
        received_oidc_details: Dict[str, _OIDCClientID],
        server_start_exception_cls: Type[Exception],
        states: List[str],
    ) -> None:
        """Tests that server start exceptions are reraised when awaited."""
        # Mock server starting to make it throw an exception
        mocker.patch.object(
            oidc_auth_flow_handler,
            "_start",
            autospec=True,
            side_effect=server_start_exception_cls("specific exception"),
        )
        oidc_auth_flow_handler.start_server()
        assert oidc_auth_flow_handler._server_start_task

        # Mock out receiving of OIDC details
        mock_modeller_mailbox.get_oidc_client_ids.return_value = received_oidc_details

        # Mock out code_verifier generation
        mock_secrets = mocker.patch(
            "bitfount.federated.transport.identity_verification.oidc.secrets",
            autospec=True,
        )
        mock_secrets.token_urlsafe.side_effect = code_verifiers

        # Mock out state generation
        mock_secrets.token_hex.side_effect = states

        # Mock out runner and web endpoint
        mock_runner = mocker.patch.object(
            oidc_auth_flow_handler, "_runner", autospec=True
        )
        mocker.patch.object(oidc_auth_flow_handler, "_oidc_endpoint", autospec=True)

        # Check expected server exception is re-raised
        with pytest.raises(server_start_exception_cls, match="specific exception"):
            await oidc_auth_flow_handler.handle(mock_modeller_mailbox)

        # Check server is still shutdown
        mock_runner.cleanup.assert_awaited()


@unit_test
class TestOIDCDeviceCodeHandler:
    """Tests for _OIDCDeviceCodeHandler."""

    @fixture
    def oidc_device_code_handler(
        self, audience: str, auth_domain: str, scopes: str
    ) -> _OIDCDeviceCodeHandler:
        """OIDC Device Code Flow challenge handler."""
        return _OIDCDeviceCodeHandler(auth_domain, scopes, audience)

    @fixture
    def device_code_endpoint(self, auth_domain: str) -> str:
        """Expected device code endpoint URL."""
        return f"https://{auth_domain}/oauth/device/code"

    @fixture
    def device_code_request(
        self,
        audience: str,
        client_id: str,
        scopes: str,
    ) -> _DeviceCodeRequestDict:
        """Expected device code request data."""
        return {
            "audience": audience,
            "client_id": client_id,
            "scope": scopes,
        }

    @fixture
    def device_code(self) -> str:
        """Device code."""
        return "someDeviceCode"

    @fixture
    def user_code(self) -> str:
        """User code."""
        return "someUserCode"

    @fixture
    def verification_uri(self, auth_domain: str) -> str:
        """Base verification URI."""
        return f"https://{auth_domain}/device"

    @fixture
    def verification_uri_complete(self, user_code: str, verification_uri: str) -> str:
        """Full verification URI with user code appended."""
        return f"{verification_uri}?user_code={user_code}"

    @fixture
    def expires_in(self) -> int:
        """When the device code expires."""
        return 900

    @fixture
    def interval(self) -> int:
        """The polling interval to use with the device code."""
        return 5

    @fixture
    def device_code_response(
        self,
        device_code: str,
        expires_in: int,
        interval: int,
        user_code: str,
        verification_uri: str,
        verification_uri_complete: str,
    ) -> _DeviceCodeResponseJSON:
        """Expected device code request response."""
        return {
            "device_code": device_code,
            "user_code": user_code,
            "verification_uri": verification_uri,
            "verification_uri_complete": verification_uri_complete,
            "expires_in": expires_in,
            "interval": interval,
        }

    @fixture
    def fake_now(self) -> datetime:
        """Static datetime.now() value for using in tests."""
        return datetime.now(timezone.utc)

    @fixture
    def mock_datetime_now(self, fake_now: datetime, mocker: MockerFixture) -> Mock:
        """Mock out datetime in oidc.py and return static value for now()."""
        mock_datetime = mocker.patch(
            "bitfount.federated.transport.identity_verification.oidc.datetime",
            autospec=True,
        )
        mock_datetime.now.return_value = fake_now
        return mock_datetime

    @fixture
    def expires_at(self, expires_in: int, fake_now: datetime) -> datetime:
        """The code expiration time as a datetime."""
        return fake_now + timedelta(seconds=expires_in)

    @fixture
    def expected_pod_device_code_details(
        self, device_code: str, expires_at: datetime, interval: int
    ) -> _PodDeviceCodeDetails:
        """Expected _PodDeviceCodeDetails to be returned."""
        return _PodDeviceCodeDetails(
            device_code=device_code,
            expires_at=expires_at,
            interval=interval,
        )

    @fixture
    def expected_modeller_device_code_details(
        self, user_code: str, verification_uri: str, verification_uri_complete: str
    ) -> _ModellerDeviceCodeDetails:
        """Expected _ModellerDeviceCodeDetails to be returned."""
        return _ModellerDeviceCodeDetails(
            user_code=user_code,
            verification_uri=verification_uri,
            verification_uri_complete=verification_uri_complete,
        )

    @fixture
    def expected_device_code_details_pair(
        self,
        expected_modeller_device_code_details: _ModellerDeviceCodeDetails,
        expected_pod_device_code_details: _PodDeviceCodeDetails,
    ) -> _DeviceCodeDetailsPair:
        """The pair of expected device code details."""
        return _DeviceCodeDetailsPair(
            expected_pod_device_code_details, expected_modeller_device_code_details
        )

    def test__verify_client_ids_successful(
        self,
        client_id: str,
        oidc_device_code_handler: _OIDCDeviceCodeHandler,
        patch_get_auth_environment: Mock,
    ) -> None:
        """Test _verify_client_ids() passes correctly."""
        oidc_details = {f"user{i}/pod{i}": _OIDCClientID(client_id) for i in range(3)}

        # Should just pass happily
        oidc_device_code_handler._verify_client_ids(oidc_details)

    def test__verify_client_ids_fails_diff_auth_domain(
        self,
        auth_domain: str,
        oidc_device_code_handler: _OIDCDeviceCodeHandler,
        patch_get_auth_environment: Mock,
    ) -> None:
        """Test _verify_client_ids() fails if auth domains differ."""
        # Change _auth_domain on the handler to induce mismatch
        oidc_device_code_handler._auth_domain = "not_the_same"

        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Mismatch between setup auth environment and current: "
                f"expected {oidc_device_code_handler._auth_domain}, got {auth_domain}"
            ),
        ):
            oidc_device_code_handler._verify_client_ids({})

    def test__verify_client_ids_fails_diff_client_ids(
        self,
        client_id: str,
        oidc_device_code_handler: _OIDCDeviceCodeHandler,
        patch_get_auth_environment: Mock,
    ) -> None:
        """Test _verify_client_ids() fails if client IDs differ."""
        # Have one "correct" client_id
        oidc_details = {
            "user0/pod0": _OIDCClientID(client_id),
        }
        # Add two "incorrect" client_ids
        incorrect_oidc_details = {
            f"user{i}/pod{i}": _OIDCClientID(f"diff_client_id_{i}") for i in range(1, 3)
        }
        oidc_details.update(incorrect_oidc_details)

        # Create expected error message
        error_pods = "; ".join(
            [
                f"Pod ID = {pod_id}, Client ID = {details.client_id}"
                for pod_id, details in incorrect_oidc_details.items()
            ]
        )
        expected_error_message = (
            f"Authorisation environments do not match. Expected client_id "
            f'"{client_id}" but the following pods mismatched: {error_pods}'
        )

        with pytest.raises(
            AuthEnvironmentError, match=re.escape(expected_error_message)
        ):
            oidc_device_code_handler._verify_client_ids(oidc_details)

    @responses.activate
    def test__get_device_code(
        self,
        client_id: str,
        device_code_endpoint: str,
        device_code_request: _DeviceCodeRequestDict,
        device_code_response: _DeviceCodeResponseJSON,
        expected_device_code_details_pair: _DeviceCodeDetailsPair,
        mock_datetime_now: Mock,
        oidc_device_code_handler: _OIDCDeviceCodeHandler,
    ) -> None:
        """Test _get_device_code() works correctly."""
        responses.add(
            responses.POST,
            url=device_code_endpoint,
            json=device_code_response,
            match=[
                matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], device_code_request)
                )
            ],
        )

        device_code_details_pair = oidc_device_code_handler._get_device_code(client_id)

        assert device_code_details_pair == expected_device_code_details_pair

    @pytest.mark.parametrize(
        argnames=("status_code", "expected_error_msg"),
        argvalues=(
            pytest.param(
                100, "Unexpected response: status_code = 100; ", id="status_code=100"
            ),
            pytest.param(
                201, "Unexpected response: status_code = 201; ", id="status_code=201"
            ),
            pytest.param(
                300, "Unexpected response: status_code = 300; ", id="status_code=300"
            ),
            pytest.param(400, "400 Client Error: ", id="status_code=400"),
            pytest.param(500, "500 Server Error: ", id="status_code=500"),
        ),
    )
    @responses.activate
    def test__get_device_code_fails_non_200_response(
        self,
        client_id: str,
        device_code_endpoint: str,
        device_code_request: _DeviceCodeRequestDict,
        expected_error_msg: str,
        oidc_device_code_handler: _OIDCDeviceCodeHandler,
        remove_web_retry_backoff_sleep: Optional[Mock],
        status_code: int,
    ) -> None:
        """Test _get_device_code() fails on non-200 response."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        # Add a randomly filled or empty body to test different responses
        body = "not json error message" if status_code % 100 else ""
        responses.add(
            responses.POST,
            url=device_code_endpoint,
            body=body,
            status=status_code,
            match=[
                matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], device_code_request)
                )
            ],
        )

        # Modify expected message if needed
        # (i.e. relevant status code and body present)
        if status_code < 400 and body:
            expected_error_msg += body

        with pytest.raises(
            HTTPError,
            match=re.escape(expected_error_msg),
        ):
            oidc_device_code_handler._get_device_code(client_id)

        # Check retries occurred if expected
        if status_code in web_utils._RETRY_STATUS_CODES:
            assert (
                remove_web_retry_backoff_sleep.call_count
                == web_utils._DEFAULT_MAX_RETRIES
            )
        else:
            remove_web_retry_backoff_sleep.assert_not_called()

    @pytest.mark.parametrize(
        argnames=("content_type", "content_value", "expected_error"),
        argvalues=(
            pytest.param("json", "wrong json type", TypeError, id="wrong_json_type"),
            pytest.param("json", {}, KeyError, id="missing_json_key"),
            pytest.param(
                "body", "not json error message", InvalidJSONError, id="not_json"
            ),
        ),
    )
    @responses.activate
    def test__get_device_code_fails_json_errors(
        self,
        client_id: str,
        content_type: Literal["json", "body"],
        content_value: str,
        device_code_endpoint: str,
        device_code_request: _DeviceCodeRequestDict,
        expected_error: Type[Exception],
        oidc_device_code_handler: _OIDCDeviceCodeHandler,
    ) -> None:
        """Test _get_device_code() fails on JSON issues in response.

        Tests with:
            - non-dict JSON
            - missing key dict JSON
            - non-JSON response
        """
        partial_response_add = functools.partial(
            responses.add,
            responses.POST,
            url=device_code_endpoint,
            match=[
                matchers.urlencoded_params_matcher(
                    cast(Dict[str, str], device_code_request)
                )
            ],
        )
        if content_type == "json":
            partial_response_add(json=content_value)
        else:
            partial_response_add(body=content_value)

        with pytest.raises(expected_error):
            oidc_device_code_handler._get_device_code(client_id)

    @pytest.mark.parametrize("num_pods_to_use", (1, 2, 3))
    async def test_handle(
        self,
        capsys: CaptureFixture,
        device_code: str,
        expires_at: datetime,
        interval: int,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        num_pods_to_use: int,
        oidc_device_code_handler: _OIDCDeviceCodeHandler,
        pod_identifiers: List[str],
        received_oidc_details: Dict[str, _OIDCClientID],
        user_code: str,
        verification_uri: str,
        verification_uri_complete: str,
    ) -> None:
        """Tests handle() method for differing numbers of pods."""
        # Patch out client ID reception
        limited_oidc_details = {
            pod_id: received_oidc_details[pod_id]
            for pod_id in pod_identifiers[:num_pods_to_use]
        }
        mock_modeller_mailbox.get_oidc_client_ids.return_value = limited_oidc_details

        # Patch out verification check
        mock_verify_client_ids = mocker.patch.object(
            oidc_device_code_handler, "_verify_client_ids", autospec=True
        )

        # Patch out device code retrieval
        device_code_details = [
            _DeviceCodeDetailsPair(
                _PodDeviceCodeDetails(
                    device_code=f"{device_code}_{i}",
                    expires_at=expires_at,
                    interval=interval,
                ),
                _ModellerDeviceCodeDetails(
                    user_code=f"{user_code}_{i}",
                    verification_uri=verification_uri,
                    verification_uri_complete=f"{verification_uri_complete}_{i}",
                ),
            )
            for i in range(num_pods_to_use)
        ]
        mocker.patch.object(
            oidc_device_code_handler,
            "_get_device_code",
            side_effect=device_code_details,
        )

        # Mock out webbrowser
        mock_webbrowser = mocker.patch(
            "bitfount.federated.transport.identity_verification.oidc.webbrowser",
            autospec=True,
        )

        # Mock out asyncio.sleep()
        mock_asyncio_sleep = mocker.patch.object(asyncio, "sleep", autospec=True)

        # Perform call
        await oidc_device_code_handler.handle(mock_modeller_mailbox)

        # Check verification occurred
        mock_verify_client_ids.assert_called_once_with(limited_oidc_details)

        # Check pod details sent as expected
        mock_modeller_mailbox.send_oidc_device_code_responses.assert_awaited_once_with(
            {
                pod_identifiers[i]: device_code_details[i].pod_details
                for i in range(num_pods_to_use)
            }
        )

        # Check URLs printed
        stdout = capsys.readouterr().out
        if num_pods_to_use == 1:
            pod_id = pod_identifiers[0]
            modeller_details = device_code_details[0].modeller_details
            user_code = modeller_details.user_code
            verification_uri_complete = modeller_details.verification_uri_complete
            assert (
                "A browser window will be opened, please login and confirm "
                "identity verification access for the pod.\n"
                "If a browser window is not opened, then please visit the "
                "following URL:\n"
                f"\tFor {pod_id}: code: {user_code}; {verification_uri_complete}"
            ) in stdout
        else:
            url_details = []
            for i in range(num_pods_to_use):
                pod_id = pod_identifiers[i]
                modeller_details = device_code_details[i].modeller_details
                user_code = modeller_details.user_code
                verification_uri_complete = modeller_details.verification_uri_complete
                url_details.append(
                    f"\tFor {pod_id}: code: {user_code}; {verification_uri_complete}"
                )
            assert (
                "Browser windows will be opened, please login and confirm "
                "identity verification access for these pods.\n"
                "If no or not all browser windows open, then please visit "
                "the following URLs:\n" + "\n".join(url_details)
            ) in stdout

        # Check sleep was called
        mock_asyncio_sleep.assert_awaited_once_with(1)

        # Check URLs opened correctly
        assert mock_webbrowser.open_new_tab.call_args_list == [
            call(device_code_details[i].modeller_details.verification_uri_complete)
            for i in range(num_pods_to_use)
        ]
