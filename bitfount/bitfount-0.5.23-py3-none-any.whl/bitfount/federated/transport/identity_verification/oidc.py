"""Handling of OIDC challenges."""
from __future__ import annotations

import asyncio
from asyncio import Task, create_task
import base64
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from typing import DefaultDict, Dict, Final, Iterator, List
from urllib.parse import urlencode
import webbrowser

from aiohttp import web
from aiohttp.web import Application, AppRunner
from aiohttp.web import Request as AioRequest
from aiohttp.web import Response as AioResponse
from aiohttp.web import TCPSite
import requests
from requests import HTTPError

from bitfount import web_utils
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.identity_verification import (
    _BITFOUNT_MODELLER_PORT,
    _PORT_WAIT_TIMEOUT,
)
from bitfount.federated.transport.identity_verification.types import (
    _HasWebServer,
    _ResponseHandler,
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
from bitfount.hub.authentication_flow import (
    _PRODUCTION_AUTH_DOMAIN,
    AuthEnvironmentError,
    _get_auth_environment,
)
from bitfount.hub.types import _DeviceCodeRequestDict, _DeviceCodeResponseJSON
from bitfount.types import _JSONDict

logger = _get_federated_logger(__name__)

# This forces `requests` to make IPv4 connections
# TODO: [BIT-1443] Remove this once Hub/AM support IPv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False  # type: ignore[attr-defined] # Reason: see above # noqa: B950

_OIDC_IDENTITY_VERIFICATION_SCOPES: Final[str] = "execute:task"
_OIDC_IDENTITY_VERIFICATION_AUDIENCE: Final[
    str
] = "https://am.bitfount.com/api/access/modellerProofOfIdentity"

_CALLBACK_ROUTE: Final[str] = "/api/auth/callback/auth0"


class _OIDCWebEndpoint:
    """Web endpoint for OIDC Authorization Code Flow callbacks."""

    def __init__(self) -> None:
        self.all_done = asyncio.Event()
        self._responses: Dict[str, _OIDCAuthEndpointResponse] = {}
        self._initialised = False

        self._id_to_state: Dict[str, str]
        self._state_to_id: Dict[str, str]
        self._urls_iter: Iterator[str]

    def initialise(self, urls: List[str], states: Dict[str, str]) -> None:
        """Initialise the endpoint with the authorize URLs and states to use.

        This has to be done post-init as the webserver takes a while to spin up
        so we want to start it early and provide the data when we are able to.
        """
        self._id_to_state = states
        self._state_to_id = {v: k for k, v in states.items()}

        self._urls_iter = iter(urls)

        self._initialised = True

    def start_processing(self) -> None:
        """Starts the processing of authorize URLs.

        Will open a webbrowser for the first one; others are then handled as redirects
        from each callback URL.
        """
        if not self._initialised:
            logger.critical(
                "OIDC callback endpoint has not been initialised. "
                "Unable to complete OIDC authentication."
            )
            raise RuntimeError(
                "OIDC callback endpoint has not been initialised. "
                "Unable to complete OIDC authentication."
            )

        first_url = next(self._urls_iter)

        # Open first authorization URL (it will autoredirect to the rest)
        logger.info(
            f"Attempting to open browser. "
            f"Running a headless client? "
            f"You'll need to open this link in a browser: {first_url}"
        )
        webbrowser.open(first_url)

    async def process_callback(self, request: AioRequest) -> AioResponse:
        """Process each authorize callback, extracting the auth code.

        Will automatically redirect to the next authorize URL in the chain until
        all have been processed.
        """
        if not self._initialised:
            logger.critical(
                "OIDC callback endpoint has not been initialised. "
                "Unable to complete OIDC authentication."
            )
            raise RuntimeError(
                "OIDC callback endpoint has not been initialised. "
                "Unable to complete OIDC authentication."
            )

        # Extract and store response details from the callback URL. The `state`
        # parameter is used to identify which pod this auth code is intended for,
        # as well as to check that the response is valid.
        query_dict = request.query
        auth_code = query_dict["code"]
        state = query_dict["state"]
        pod_id = self._state_to_id[state]
        self._responses[pod_id] = _OIDCAuthEndpointResponse(auth_code, state)

        # Get next /authorize URL to go to
        try:
            next_url = next(self._urls_iter)
            # aiohttp uses an exception to return a redirect response
            raise web.HTTPFound(next_url)
        except StopIteration:
            # All URLs visited, mark done
            self.all_done.set()
            return AioResponse(
                text="You've now proven your identity to all pods involved in the "
                "task. You can close this tab."
            )

    async def get_responses(self) -> Dict[str, _OIDCAuthEndpointResponse]:
        """Get the responses to each authorize call.

        Will wait until all calls have completed.
        """
        await self.all_done.wait()
        return self._responses


def _get_urlsafe_hash(s: str, initial_encoding: str = "utf-8") -> str:
    """Generate a URL-safe hash of a string.

    Encodes the string initially using the provided encoding, finds the sha256
    hash of this, b64-urlencodes the hash digest, and removes the padding "=" that
    python keeps in there.
    """
    encoded_s: bytes = s.encode(initial_encoding)
    sha256_hash: bytes = hashlib.sha256(encoded_s).digest()
    b64_hash: bytes = base64.urlsafe_b64encode(sha256_hash)
    b64_hash_str: str = b64_hash.decode("utf-8").replace("=", "")
    return b64_hash_str


def _verify_client_ids(
    oidc_details: Dict[str, _OIDCClientID], expected_auth_domain: str
) -> None:
    """Checks that all received client IDs match the expected one.

    Raises:
        AuthEnvironmentError:
            If the Client IDs for this auth environment do not match those
            received from the pods.
    """
    our_auth_env = _get_auth_environment()

    if expected_auth_domain != our_auth_env.auth_domain:
        raise ValueError(
            f"Mismatch between setup auth environment and current: "
            f"expected {expected_auth_domain}, got {our_auth_env.auth_domain}"
        )

    errors = [
        (pod_id, details)
        for pod_id, details in oidc_details.items()
        if details.client_id != our_auth_env.client_id
    ]
    if errors:
        errors_str = "; ".join(
            [
                f"Pod ID = {pod_id}, Client ID = {details.client_id}"
                for pod_id, details in errors
            ]
        )
        raise AuthEnvironmentError(
            f"Authorisation environments do not match. "
            f'Expected client_id "{our_auth_env.client_id}" but the following '
            f"pods mismatched: {errors_str}"
        )


class _OIDCAuthFlowChallengeHandler(_ResponseHandler, _HasWebServer):
    """Perform OIDC flow from the modeller-side.

    This flow is based on:
    https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-proof-key-for-code-exchange-pkce  # noqa: B950
    """

    def __init__(
        self,
        auth_domain: str = _PRODUCTION_AUTH_DOMAIN,
        scopes: str = _OIDC_IDENTITY_VERIFICATION_SCOPES,
        audience: str = _OIDC_IDENTITY_VERIFICATION_AUDIENCE,
    ):
        self._auth_domain = auth_domain
        self._authorize_endpoint = f"https://{self._auth_domain}/authorize"
        self._redirect_uri = (
            f"http://localhost:{_BITFOUNT_MODELLER_PORT}{_CALLBACK_ROUTE}"
        )

        self._scopes: str = scopes
        self._audience: str = audience

        # Create web application for callbacks
        self._oidc_endpoint = _OIDCWebEndpoint()
        app = Application()
        app.add_routes([web.get(_CALLBACK_ROUTE, self._oidc_endpoint.process_callback)])
        self._runner = AppRunner(app)

        # This task is used to ensure we don't try to
        # perform authentication before the server has started
        self._server_start_task: Task

    def start_server(self) -> Task:
        """Sets up and starts the web server."""
        self._server_start_task = create_task(self._start())
        return self._server_start_task

    async def _start(self) -> None:
        """Sets up and starts the web server."""
        logger.debug("Starting OIDC web server")
        host = "localhost"
        port = _BITFOUNT_MODELLER_PORT

        # Try to create web server for endpoint, failing out if binding to the
        # host and port isn't possible.
        try:
            await self._runner.setup()
            # This site is accessed by the modeller (who is running this code)
            # in their own browser.
            # Their OIDC IdP provider will redirect them to:
            # `http://localhost:{BITFOUNT_MODELLER_PORT}/{_CALLBACK_ROUTE}`
            # So they should not have any issues accessing it.
            site = TCPSite(self._runner, host, port)
            # wait_for() use ensures we don't hang indefinitely on waiting for the
            # port to be available
            await asyncio.wait_for(site.start(), _PORT_WAIT_TIMEOUT)
        except TimeoutError as e:
            logger.critical(
                f"Timeout reached whilst trying to bind OIDC web endpoint to "
                f"http://{host}:{port}"
            )
            raise e
        except OSError as e:
            # Raises OSError: [Errno 48] if address already in use
            logger.critical(f"Unable to bind OIDC web endpoint to http://{host}:{port}")
            raise e

        logger.debug("OIDC web server started successfully")

    async def handle(self, modeller_mailbox: _ModellerMailbox) -> None:
        """Receive and perform OIDC verification."""
        try:
            # Check that start_server() has been called
            try:
                self._server_start_task
            except AttributeError:
                raise RuntimeError(
                    "OIDC server has not been started; "
                    "ensure start_server() has been called."
                )

            # Await Client ID information from pods
            oidc_details = await modeller_mailbox.get_oidc_client_ids()

            # Verify Client IDs are as expected
            self._verify_client_ids(oidc_details)

            # Generate /authorize URL for each authorization request
            to_send_dicts: DefaultDict[str, _JSONDict] = defaultdict(dict)
            urls: Dict[str, str] = {}
            states: Dict[str, str] = {}
            for pod_id, details in oidc_details.items():
                # Generate code verifier
                # Should be between 43 and 128 characters; recommended to use
                # base64url-encoding which secrets.token_urlsafe does for us. 60 bytes
                # will produce ~78 characters.
                # See: https://datatracker.ietf.org/doc/html/rfc7636#section-4.1
                code_verifier: str = secrets.token_urlsafe(nbytes=60)
                # Add to details
                to_send_dicts[pod_id]["code_verifier"] = code_verifier

                # Generate code challenge
                # This is the b64url-encoded SHA256 hash of the ascii-encoded
                # code_verifier.
                # We also encode the bytes-output of the b64 encoding with UTF-8 to
                # make it a string.
                # See: https://datatracker.ietf.org/doc/html/rfc7636#section-4.2
                code_challenge: str = _get_urlsafe_hash(
                    code_verifier, initial_encoding="ascii"
                )

                # Request PKCE authorization
                # Generate random state
                state = secrets.token_hex(nbytes=32)
                params = urlencode(
                    {
                        "audience": self._audience,
                        "scope": self._scopes,
                        "response_type": "code",
                        "client_id": details.client_id,
                        "state": state,
                        "redirect_uri": self._redirect_uri,
                        "code_challenge_method": "S256",
                        "code_challenge": code_challenge,
                    }
                )
                url = self._authorize_endpoint + f"?{params}"

                urls[pod_id] = url
                states[pod_id] = state

            # Set generated URLs on web endpoint for later iteration
            urls_list: List[str] = list(urls.values())
            self._oidc_endpoint.initialise(urls_list, states)

            # Wait for server if necessary
            if not self._server_start_task.done():
                logger.info("Waiting for OIDC challenge handler to start")
                await self._server_start_task
            # If an exception was thrown in the task,
            # Task.result() will re-raise it for us.
            self._server_start_task.result()

            # Start URL processing
            self._oidc_endpoint.start_processing()

            # Wait for all authorization to be done
            responses = await self._oidc_endpoint.get_responses()

            # Validate the states are the same
            for pod_id, response in responses.items():
                if response.state != states[pod_id]:
                    raise ValueError(
                        f"Unable to validate response intended for {pod_id}"
                    )

            # Add auth_code and redirect_uri to details
            for pod_id in oidc_details:
                to_send_dicts[pod_id]["auth_code"] = responses[pod_id].auth_code
                to_send_dicts[pod_id]["redirect_uri"] = self._redirect_uri

            # Send details to pods
            to_send: Dict[str, _OIDCAuthFlowResponse] = {
                pod_id: _OIDCAuthFlowResponse(**d)
                for pod_id, d in to_send_dicts.items()
            }
            await modeller_mailbox.send_oidc_auth_flow_responses(to_send)
        finally:
            await self.stop_server()

    def _verify_client_ids(self, oidc_details: Dict[str, _OIDCClientID]) -> None:
        """Checks that all received client IDs match the expected one.

        Raises:
            AuthEnvironmentError:
                If the Client IDs for this auth environment do not match those
                received from the pods.
        """
        return _verify_client_ids(oidc_details, expected_auth_domain=self._auth_domain)

    async def stop_server(self) -> None:
        """Stop the web server."""
        await self._runner.cleanup()


class _OIDCDeviceCodeHandler(_ResponseHandler):
    """OIDC Device Authorisation Flow from modeller-side.

    See: https://auth0.com/docs/get-started/authentication-and-authorization-flow/device-authorization-flow  # noqa: B950
    """

    def __init__(
        self,
        auth_domain: str = _PRODUCTION_AUTH_DOMAIN,
        scopes: str = _OIDC_IDENTITY_VERIFICATION_SCOPES,
        audience: str = _OIDC_IDENTITY_VERIFICATION_AUDIENCE,
    ):
        self._auth_domain = auth_domain
        self._device_code_endpoint = f"https://{self._auth_domain}/oauth/device/code"

        self._scopes: str = scopes
        self._audience: str = audience

    async def handle(self, modeller_mailbox: _ModellerMailbox) -> None:
        """See parent class for more information."""
        logger.debug("Getting oidc client ids")
        # Await Client ID information from pods
        oidc_details = await modeller_mailbox.get_oidc_client_ids()

        # Verify Client IDs are as expected
        self._verify_client_ids(oidc_details)

        # Get device code details for each pod
        logger.info("Retrieving device codes for identity verification.")
        device_codes: Dict[str, _DeviceCodeDetailsPair] = {}
        for pod_id, details in oidc_details.items():
            device_codes[pod_id] = self._get_device_code(details.client_id)

        # Send relevant details to pods
        logger.info("Sending identity verification details to pods")
        await modeller_mailbox.send_oidc_device_code_responses(
            {pod_id: details.pod_details for pod_id, details in device_codes.items()}
        )

        # Get user to approve the access requests
        # Print details about what's happening
        if len(device_codes) > 1:
            browser_opened_str = (
                "Browser windows will be opened, please login and confirm "
                "identity verification access for these pods."
            )
            cli_str = (
                "If no or not all browser windows open, then please visit "
                "the following URLs:"
            )
        else:
            browser_opened_str = (
                "A browser window will be opened, please login and confirm "
                "identity verification access for the pod."
            )
            cli_str = (
                "If a browser window is not opened, then please visit the "
                "following URL:"
            )
        print(browser_opened_str)
        print(cli_str)

        # Print user code details so they know what to verify and the URIs so they
        # can manually open them if needed.
        to_open = []
        for pod_id, device_code_details in device_codes.items():
            verification_uri_complete = (
                device_code_details.modeller_details.verification_uri_complete
            )
            user_code = device_code_details.modeller_details.user_code

            print(f"\tFor {pod_id}: code: {user_code}; {verification_uri_complete}")
            to_open.append(verification_uri_complete)

        # Give user time to see the codes, so they know what to verify
        await asyncio.sleep(1)

        # Open all URIs
        for uri in to_open:
            webbrowser.open_new_tab(uri)

    def _verify_client_ids(self, oidc_details: Dict[str, _OIDCClientID]) -> None:
        """Checks that all received client IDs match the expected one.

        Raises:
            AuthEnvironmentError:
                If the Client IDs for this auth environment do not match those
                received from the pods.
        """
        return _verify_client_ids(oidc_details, expected_auth_domain=self._auth_domain)

    def _get_device_code(self, client_id: str) -> _DeviceCodeDetailsPair:
        logger.debug(f"Retrieving device code for client id: {client_id}")
        # Make request and raise for error if needed
        request_data: _DeviceCodeRequestDict = {
            "audience": self._audience,
            "scope": self._scopes,
            "client_id": client_id,
        }
        response = web_utils.post(
            self._device_code_endpoint,
            data=request_data,
        )

        # Handle 4XX/5XX errors
        response.raise_for_status()

        # Handle other non-200 errors
        if (status_code := response.status_code) != 200:
            raise HTTPError(
                f"Unexpected response: status_code = {status_code}; {response.text}"
            )

        response_json: _DeviceCodeResponseJSON = response.json()

        # Calculate expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=response_json["expires_in"]
        )

        return _DeviceCodeDetailsPair(
            _PodDeviceCodeDetails(
                device_code=response_json["device_code"],
                expires_at=expires_at,
                interval=response_json["interval"],
            ),
            _ModellerDeviceCodeDetails(
                user_code=response_json["user_code"],
                verification_uri=response_json["verification_uri"],
                verification_uri_complete=response_json["verification_uri_complete"],
            ),
        )
