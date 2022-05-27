"""Test SAML handling."""
import asyncio
from asyncio import Task, create_task
import re
from typing import Dict, List, Type
from unittest.mock import Mock, create_autospec

from _pytest.logging import LogCaptureFixture
from aiohttp import web
from aiohttp.pytest_plugin import AiohttpClient
from aiohttp.test_utils import TestClient
from aiohttp.web_app import Application
from aiohttp.web_runner import AppRunner, TCPSite
import pytest
from pytest import fixture
from pytest_mock import MockerFixture

from bitfount.federated.transport.base_transport import _WorkerMailboxDetails
from bitfount.federated.transport.identity_verification import _BITFOUNT_MODELLER_PORT
from bitfount.federated.transport.identity_verification.saml import (
    _SAMLChallengeHandler,
    _SAMLWebEndpoint,
)
from bitfount.federated.transport.message_service import (
    _BitfountMessageType,
    _DecryptedBitfountMessage,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.types import _SAMLResponse
from tests.utils.helper import get_critical_logs, unit_test
from tests.utils.mocks import AwaitableMock


@fixture
def saml_challenges_count() -> int:
    """Number of SAML challenges."""
    return 3


@fixture
def saml_challenges(saml_challenges_count: int) -> List[_DecryptedBitfountMessage]:
    """SAML Challenges."""
    return [
        _DecryptedBitfountMessage(
            message_type=_BitfountMessageType.SAML_REQUEST,
            body=f"saml-challenge-{i}",
            recipient="modeller",
            recipient_mailbox_id="modeller-mailbox-id",
            sender=f"sender-{i}",
            sender_mailbox_id=f"sender-mailbox-{i}",
        )
        for i in range(saml_challenges_count)
    ]


@fixture
def saml_responses(saml_challenges_count: int) -> List[Dict[str, str]]:
    """SAML Responses from IDP."""
    return [{"saml": f"token-{i}"} for i in range(saml_challenges_count)]


@fixture
def mailbox_details(
    saml_challenges: List[_DecryptedBitfountMessage],
) -> Dict[str, _WorkerMailboxDetails]:
    """Pod ID to Mailbox details map."""
    return {
        message.sender: _WorkerMailboxDetails(
            pod_identifier=message.sender,
            public_key=Mock(),
            mailbox_id=message.sender_mailbox_id,
            aes_encryption_key=f"aes-key-{message.sender}".encode(),
        )
        for message in saml_challenges
    }


@fixture
def idp_url() -> str:
    """IDP URL."""
    return "http://unit-test.saml-idp.bitfount.com/path?SAMLResponse="


@unit_test
class TestSAMLWebEndpoint:
    """Test the handling of SAML Challenges."""

    @fixture
    def challenges_handled_event(self) -> asyncio.Event:
        """An asyncio Event to mark when all challenges are handled."""
        return asyncio.Event()

    @fixture
    def endpoint(
        self, challenges_handled_event: asyncio.Event, idp_url: str
    ) -> _SAMLWebEndpoint:
        """The SAML Web Endpoint to test against."""
        return _SAMLWebEndpoint(challenges_handled_event, idp_url)

    @fixture
    def aiohttp_app(self, endpoint: _SAMLWebEndpoint) -> Application:
        """Test AioHTTP application."""
        app = Application()
        app.add_routes([web.post("/api/saml", endpoint.handle_saml_idp_response)])
        return app

    @fixture
    async def client(
        self, aiohttp_app: Application, aiohttp_client: AiohttpClient
    ) -> TestClient:
        """Test client for AioHTTP interactions."""
        return await aiohttp_client(aiohttp_app)

    async def test_saml_responses_are_accumulated(
        self,
        aiohttp_app: Application,
        challenges_handled_event: asyncio.Event,
        client: TestClient,
        endpoint: _SAMLWebEndpoint,
        idp_url: str,
        mailbox_details: Dict[str, _WorkerMailboxDetails],
        saml_challenges: List[_DecryptedBitfountMessage],
        saml_responses: List[Dict[str, str]],
    ) -> None:
        """Test that we block and gather SAML responses from IdPs.

        This is testing that we don't shut down the server until
        all IdP responses have been received by the web server.
        This is achieved using an asyncio.Event().

        We also ensure that the web server redirects us to the
        next SAML URL.

        We also check that the saml responses are all passed
        to a function which will send them to the corresponding
        pods.
        """
        accumulated_saml_responses = []

        async def sender(
            saml_response: _SAMLResponse,
            _mailbox_details: _WorkerMailboxDetails,
        ) -> None:
            """Fake sending function.

            We use this to easily check that our SAML responses
            would be sent to the correct pods.
            """
            accumulated_saml_responses.append((saml_response, _mailbox_details))

        endpoint.set_saml_challenges(
            list(zip(saml_challenges, mailbox_details.values())), sender
        )

        # These requests would normally be made by the users browser
        # First SAML challenge Response
        first_redirect = await client.post(
            "/api/saml", data=saml_responses[0], allow_redirects=False
        )
        assert not challenges_handled_event.is_set()
        # The first redirect is for 2nd request,
        # as the first one would have been opened in the browser
        # The SAML response from the first challenge was sent in the POST above
        assert first_redirect.headers["location"] == f"{idp_url}saml-challenge-1"

        # Second SAML response
        second_redirect = await client.post(
            "/api/saml", data=saml_responses[1], allow_redirects=False
        )
        assert not challenges_handled_event.is_set()
        assert second_redirect.headers["location"] == f"{idp_url}saml-challenge-2"

        # Third SAML response
        success_page = await client.post("/api/saml", data=saml_responses[2])
        # The event should have occurred so that the web server can be shut down
        # And the modeller can go ahead with the rest of the flow
        assert challenges_handled_event.is_set()
        assert str(success_page.url.path) == "/api/saml"
        page_text = await success_page.text()
        assert (
            page_text == "You've now proven your identity to all pods involved"
            " in the task. You can close this tab."
        )

        await aiohttp_app.cleanup()

        # Check that send was called with the expected responses and mailboxes
        assert accumulated_saml_responses == list(
            zip(saml_responses, mailbox_details.values())
        )

    async def test_handle_throws_exception_when_not_configured(
        self, idp_url: str
    ) -> None:
        """Test exception thrown when send not set."""
        endpoint = _SAMLWebEndpoint(asyncio.Event(), idp_url)

        with pytest.raises(
            RuntimeError,
            match="SAML Challenges & Send method were not set "
            "in SAMLWebEndpoint. Unable to complete SAML"
            " authentication.",
        ):
            await endpoint.handle_saml_idp_response(Mock())


@unit_test
class TestSAMLChallengeHandler:
    """Test SAMLChallengeHandler."""

    @fixture
    def saml_challenge_handler(self, idp_url: str) -> _SAMLChallengeHandler:
        """Handler to use in tests."""
        return _SAMLChallengeHandler(idp_url)

    @fixture
    def mock_modeller_mailbox(
        self, mailbox_details: Dict[str, _WorkerMailboxDetails]
    ) -> Mock:
        """Mock _ModellerMailbox instance."""
        mock_mailbox: Mock = create_autospec(_ModellerMailbox, instance=True)
        mock_mailbox.worker_mailboxes = mailbox_details
        return mock_mailbox

    async def test_start_server_sets_server_start_task(
        self,
        saml_challenge_handler: _SAMLChallengeHandler,
    ) -> None:
        """Tests that the server start task is set.

        Nothing is mocked here, to ensure that the calls
        to aiohttp actually work!
        """
        saml_challenge_handler.start_server()

        assert saml_challenge_handler._server_start_task

    async def test__start_aiohttp_calls_work(
        self,
        saml_challenge_handler: _SAMLChallengeHandler,
    ) -> None:
        """Tests that the server start calls work.

        Nothing is mocked here, to ensure that the calls
        to aiohttp actually work!
        """
        await saml_challenge_handler._start()

    async def test__start_times_out_after_time(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        saml_challenge_handler: _SAMLChallengeHandler,
    ) -> None:
        """Tests that _start() will timeout if server start hangs."""
        # Mock out runner
        mock_runner = mocker.patch.object(
            saml_challenge_handler, "runner", autospec=True
        )

        # Mock out site start-up method and init
        mock_tcp_site = create_autospec(TCPSite)
        mock_tcp_site_init = mocker.patch(
            "bitfount.federated.transport.identity_verification.saml.TCPSite",
            autospec=True,
            return_value=mock_tcp_site,
        )

        # Make wait_for raise timeout exception
        mocker.patch.object(
            asyncio, "wait_for", side_effect=TimeoutError("custom timeout")
        )

        with pytest.raises(TimeoutError, match="custom timeout"):
            await saml_challenge_handler._start()

        # Check setup called and site created
        mock_runner.setup.assert_awaited_once()
        mock_tcp_site_init.assert_called_once()

        # Check logged exception
        critical_logs = get_critical_logs(caplog)
        assert (
            "Timeout reached whilst trying to bind SAML web endpoint" in critical_logs
        )

    async def test__start_handles_address_in_use_error(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        saml_challenge_handler: _SAMLChallengeHandler,
    ) -> None:
        """Tests that _start() handles address being unavailable."""
        # Mock out runner
        mock_runner = mocker.patch.object(
            saml_challenge_handler, "runner", autospec=True
        )

        # Mock out site start-up method and init
        mock_tcp_site = create_autospec(TCPSite)
        mock_tcp_site_init = mocker.patch(
            "bitfount.federated.transport.identity_verification.saml.TCPSite",
            autospec=True,
            return_value=mock_tcp_site,
        )
        # Make site.start() raise error indicating address unavailable
        mock_tcp_site.start.side_effect = OSError()

        with pytest.raises(OSError):
            await saml_challenge_handler._start()

        # Check setup called and site created
        mock_runner.setup.assert_awaited_once()
        mock_tcp_site_init.assert_called_once()

        # Check logged exception
        critical_logs = get_critical_logs(caplog)
        assert "Unable to bind SAML web endpoint" in critical_logs

    async def test_start_server_sets_up_server_in_background(
        self,
        mocker: MockerFixture,
        saml_challenge_handler: _SAMLChallengeHandler,
    ) -> None:
        """Ensure server is started in background with expected settings."""
        mock_tcp_site = mocker.patch(
            "bitfount.federated.transport.identity_verification.saml.TCPSite",
            autospec=True,
        )
        mock_create_task = mocker.patch(
            "bitfount.federated.transport.identity_verification.saml.create_task",
            wraps=create_task,
        )

        saml_challenge_handler.start_server()
        # Await start task to give time for background to run
        await saml_challenge_handler._server_start_task

        mock_create_task.assert_called_once()
        mock_tcp_site.assert_called_once_with(
            saml_challenge_handler.runner, "localhost", _BITFOUNT_MODELLER_PORT
        )
        mock_tcp_site.return_value.start.assert_awaited_once()

    async def test_saml_challenge_handler_opens_first_challenge(
        self,
        idp_url: str,
        mailbox_details: Dict[str, _WorkerMailboxDetails],
        mocker: MockerFixture,
        saml_challenge_handler: _SAMLChallengeHandler,
        saml_challenges: List[_DecryptedBitfountMessage],
    ) -> None:
        """Tests that the SAML authentication flow is triggered.

        This ensures that we set up the SAMLWebEndpoint as expected,
        and that we open a browser to begin the SAML auth flow.

        It also checks that we shut down our web server.
        """
        mock_endpoint = create_autospec(_SAMLWebEndpoint, instance=True)
        saml_challenge_handler.saml_endpoint = mock_endpoint

        challenges_handled = asyncio.Event()
        saml_challenge_handler.all_saml_challenges_handled = challenges_handled

        mock_webbrowser = mocker.patch(
            "bitfount.federated.transport.identity_verification.saml.webbrowser"
        )
        # Set event; mimicking the side effect of the listener
        mock_webbrowser.open.side_effect = lambda _: challenges_handled.set()

        # Mock the server start task
        saml_challenge_handler._server_start_task = AwaitableMock(spec=Task)
        saml_challenge_handler._server_start_task.done.return_value = False
        saml_challenge_handler.runner = create_autospec(AppRunner, instance=True)
        mock_send = Mock()

        await saml_challenge_handler._handle_saml_challenges(
            mock_send, saml_challenges, mailbox_details
        )

        # Ensure browser is opened to the first SAML URL
        mock_webbrowser.open.assert_called_once_with(
            f"{idp_url}{saml_challenges[0].body}"
        )
        # Ensure the web endpoint is given the SAML challenges
        mock_endpoint.set_saml_challenges.assert_called_once_with(
            list(zip(saml_challenges, mailbox_details.values())), mock_send
        )

        # Check that server task was awaited and interacted with
        saml_challenge_handler._server_start_task.done.assert_called_once()
        saml_challenge_handler._server_start_task.assert_awaited_once()
        saml_challenge_handler._server_start_task.result.assert_called_once()

    async def test_handle_method(
        self,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        saml_challenge_handler: _SAMLChallengeHandler,
        saml_challenges: List[_DecryptedBitfountMessage],
    ) -> None:
        """Tests that the handle() method performs expected operations.

        In particular that it awaits the SAML challenges being sent and then
        passes these off to be handled.
        """
        # Mock out runner
        mock_runner = mocker.patch.object(
            saml_challenge_handler, "runner", autospec=True
        )

        # Create mock ModellerMailbox
        mock_modeller_mailbox.get_saml_challenges.return_value = saml_challenges

        # Mock out _handle_saml_challenges method
        mock__handle_saml_challenges = mocker.patch.object(
            saml_challenge_handler, "_handle_saml_challenges", autospec=True
        )

        await saml_challenge_handler.handle(mock_modeller_mailbox)

        # Check SAML challenges awaited
        mock_modeller_mailbox.get_saml_challenges.assert_awaited_once()
        # Check passed on to actual handler
        mock__handle_saml_challenges.assert_awaited_once_with(
            mock_modeller_mailbox.send_saml_responses,
            saml_challenges,
            mock_modeller_mailbox.worker_mailboxes,
        )
        # Check server shutdown at end
        mock_runner.cleanup.assert_awaited()

    async def test_handle_fails_if_server_not_started(
        self,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        saml_challenge_handler: _SAMLChallengeHandler,
        saml_challenges: List[_DecryptedBitfountMessage],
    ) -> None:
        """Tests handle() fails if server not started."""
        # Mock out runner
        mock_runner = mocker.patch.object(
            saml_challenge_handler, "runner", autospec=True
        )

        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "SAML server has not been started; "
                "ensure start_server() has been called."
            ),
        ):
            await saml_challenge_handler.handle(mock_modeller_mailbox)

        # Check server is still shutdown
        mock_runner.cleanup.assert_awaited()

    @pytest.mark.parametrize(
        argnames="server_start_exception_cls",
        argvalues=(TimeoutError, OSError, Exception),
    )
    async def test_handle_reraises_exception_from_start_task(
        self,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        saml_challenge_handler: _SAMLChallengeHandler,
        saml_challenges: List[_DecryptedBitfountMessage],
        server_start_exception_cls: Type[Exception],
    ) -> None:
        """Tests that server start exceptions are reraised when awaited."""
        # Mock server starting to make it throw an exception
        mocker.patch.object(
            saml_challenge_handler,
            "_start",
            autospec=True,
            side_effect=server_start_exception_cls("specific exception"),
        )
        saml_challenge_handler.start_server()
        assert saml_challenge_handler._server_start_task

        # Mock out runner and web endpoint
        mock_runner = mocker.patch.object(
            saml_challenge_handler, "runner", autospec=True
        )
        mocker.patch.object(saml_challenge_handler, "saml_endpoint", autospec=True)

        # Mock out SAML challenge reception
        mock_modeller_mailbox.get_saml_challenges.return_value = saml_challenges

        with pytest.raises(server_start_exception_cls):
            await saml_challenge_handler.handle(mock_modeller_mailbox)

        # Check server shutdown at end
        mock_runner.cleanup.assert_awaited()
