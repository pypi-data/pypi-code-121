"""Handling of SAML Challenges."""
import asyncio
from asyncio import Task, create_task
from typing import Awaitable, Callable, List, Mapping, MutableSequence, Optional, Tuple
import urllib.parse
import webbrowser

from aiohttp import web
from aiohttp.web import Application, AppRunner, Request, Response, TCPSite

from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.base_transport import _WorkerMailboxDetails
from bitfount.federated.transport.identity_verification import (
    _BITFOUNT_MODELLER_PORT,
    _PORT_WAIT_TIMEOUT,
)
from bitfount.federated.transport.identity_verification.types import (
    _HasWebServer,
    _ResponseHandler,
)
from bitfount.federated.transport.message_service import _DecryptedBitfountMessage
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.types import _SAMLResponse

logger = _get_federated_logger(__name__)


class _SAMLWebEndpoint:
    """SAML Web Listener Endpoint.

    This is an HTTP server which listens for requests
    from the user's browser when it is redirected to
    localhost by their identity provider(s).

    As each SAML response is received they are forwarded
    on to the pod that issued the matching challenge.

    Args:
        all_saml_challenges_handled:
            An Event that will be set to complete when
            all SAML challenges have been handled.
        idp_url:
            The URL of the Identity Provider.
    """

    def __init__(
        self,
        all_saml_challenges_handled: asyncio.Event,
        idp_url: str,
    ):
        self.all_saml_challenges_handled = all_saml_challenges_handled
        self.idp_url = idp_url

        self.challenges_with_mailbox_details: MutableSequence[
            Tuple[_DecryptedBitfountMessage, _WorkerMailboxDetails]
        ] = []
        self.send: Optional[
            Callable[[_SAMLResponse, _WorkerMailboxDetails], Awaitable[None]]
        ] = None

    def set_saml_challenges(
        self,
        challenges_with_mailbox_details: MutableSequence[
            Tuple[_DecryptedBitfountMessage, _WorkerMailboxDetails]
        ],
        send: Callable[[_SAMLResponse, _WorkerMailboxDetails], Awaitable[None]],
    ) -> None:
        """Prepare SAMLWebEndpoint with challenges.

        As aiohttp can't have routes added dynamically,
        and we start up our server before we receive the SAML challenges,
        this method is needed to set the challenges and send function
        once we have received the challenges and have set up a way
        to send to the task mailboxes.

        Args:
            challenges_with_mailbox_details: SAML challenge and the
                worker mailbox details for the worker that sent it.
            send: A function for sending SAML responses to workers.
        """
        self.challenges_with_mailbox_details = challenges_with_mailbox_details
        self.send = send

    async def handle_saml_idp_response(self, request: Request) -> Response:
        """Endpoint for handling SAML responses.

        This can be seen as a recursive endpoint/function.

        Args:
            request (Request): The  aiohttp web request

        Returns:
            There are two cases:
            - Base Case (Stops the recursion):
                When? We've handled all SAML Challenges.
                Returns a Web Response showing a success message
            - Recursive Case:
                When? There's outstanding SAML Challenges
                Returns a Web Response that redirects to this
                endpoint, but with the next available SAML challenge
                Removes a SAML challenge from the list.
        """
        if self.send is None:
            logger.critical(
                "SAML Challenges & Send method were not set in SAMLWebEndpoint."
                " Unable to complete SAML authentication."
            )
            raise RuntimeError(
                "SAML Challenges & Send method were not set in SAMLWebEndpoint."
                " Unable to complete SAML authentication."
            )

        # Extract SAML response from request
        saml_response: _SAMLResponse = dict(await request.post())
        # Find where we need to send SAML response
        # And remove the challenge from the list,
        # so that next iteration we process a different SAML challenge
        _, worker_mailbox = self.challenges_with_mailbox_details.pop(0)
        logger.info(
            f"Responding to SAML challenge from: {worker_mailbox.pod_identifier}"
        )
        # Send SAML response Pod that issued challenge
        await self.send(saml_response, worker_mailbox)

        if len(self.challenges_with_mailbox_details) == 0:
            # All challenges have been processed
            # So we can allow server clean up
            # And show a message in the browser
            logger.debug(
                "All SAML Challenges from Pods handled, "
                "displaying next steps in browser."
            )
            # All challenges handled so we can set the event
            self.all_saml_challenges_handled.set()
            return Response(
                text="You've now proven your identity "
                "to all pods involved in the task. "
                "You can close this tab."
            )

        # Handle the next SAML challenge in the list by redirecting
        # The user to the IdP with the next SAML challenge
        # The IdP will redirect back to this endpoint
        next_challenge, _ = self.challenges_with_mailbox_details[0]
        saml_url = f"{self.idp_url}{urllib.parse.quote_plus(next_challenge.body)}"
        logger.info(
            f"Redirecting to the next SAML Challenge. "
            f"If something goes wrong with your authentication "
            f"then visit this URL to try again: {saml_url}"
        )
        # aiohttp uses an exception to return a redirect response
        raise web.HTTPFound(saml_url)


class _SAMLChallengeHandler(_ResponseHandler, _HasWebServer):
    """Manages SAML user authentication.

    This is used to configure and perform SAML auth
    when challenges are received from resources.

    It can start, handle & shutdown a server for
    receiving SAML authentication information.
    """

    def __init__(
        self,
        idp_url: str,
    ):
        self.idp_url = idp_url

        # This event is used to prevent us from shutting down the
        # web server until all SAML challenges have been processed
        self.all_saml_challenges_handled = asyncio.Event()

        # This task is used to ensure we don't try to
        # perform SAML authentication before the server has started
        self._server_start_task: Task

        app = Application()
        # We have to create this now so that it can be added as a route
        # As Routes cannot be added in aiohttp after the runner setup
        # has been called
        self.saml_endpoint = _SAMLWebEndpoint(
            self.all_saml_challenges_handled,
            self.idp_url,
        )
        app.add_routes(
            [web.post("/api/saml", self.saml_endpoint.handle_saml_idp_response)]
        )
        self.runner = AppRunner(app)

    def start_server(self) -> Task:
        """Sets up and starts the web server."""
        self._server_start_task = create_task(self._start())
        return self._server_start_task

    async def _start(self) -> None:
        """Sets up and starts the web server."""
        logger.debug("Starting SAML web server")
        host = "localhost"
        port = _BITFOUNT_MODELLER_PORT

        # Try to create web server for endpoint, failing out if binding to the
        # host and port isn't possible.
        try:
            await self.runner.setup()
            # This site is access by the modeller (who is running this code)
            # in their own browser.
            # Their SAML IdP provider will redirect them to:
            # `http://localhost:{BITFOUNT_MODELLER_PORT}/{PATH}`
            # So they should not have any issues accessing it
            site = TCPSite(self.runner, host, port)
            # wait_for() use ensures we don't hang indefinitely on waiting for the
            # port to be available
            await asyncio.wait_for(site.start(), _PORT_WAIT_TIMEOUT)
        except TimeoutError as e:
            logger.critical(
                f"Timeout reached whilst trying to bind SAML web endpoint to "
                f"http://{host}:{port}"
            )
            raise e
        except OSError as e:
            # Raises OSError: [Errno 48] if address already in use
            logger.critical(f"Unable to bind SAML web endpoint to http://{host}:{port}")
            raise e

        logger.debug("SAML web server started successfully")

    async def _handle_saml_challenges(
        self,
        send: Callable[[_SAMLResponse, _WorkerMailboxDetails], Awaitable[None]],
        saml_challenges: MutableSequence[_DecryptedBitfountMessage],
        worker_mailbox_details: Mapping[str, _WorkerMailboxDetails],
    ) -> None:
        """Begins the process for handling SAML Challenges.

        Updates the SAMLWebEndpoint so that it's aware of the challenges.
        Opens the first challenge in the user's browser.

        Args:
            send: Function for sending SAML response to pod.
            saml_challenges: SAML Challenges from pods.
            worker_mailbox_details: Mailbox details for each pod.
        """
        # Check that start_server() has been called
        try:
            self._server_start_task
        except AttributeError:
            raise RuntimeError(
                "SAML server has not been started; "
                "ensure start_server() has been called."
            )

        # We only open the first one, then use
        # the browser to redirect us to the other pages
        # We pair the challenges with the mailbox details
        # so that we have easy access to the keys later
        challenges_with_mailbox_details: List[
            Tuple[_DecryptedBitfountMessage, _WorkerMailboxDetails]
        ] = [
            (saml_challenge, worker_mailbox_details[saml_challenge.sender])
            for saml_challenge in saml_challenges
        ]
        self.saml_endpoint.set_saml_challenges(challenges_with_mailbox_details, send)

        if not self._server_start_task.done():
            logger.info("Waiting for SAML challenge handler to start")
            await self._server_start_task
        # If an exception was thrown in the task,
        # Task.result() will re-raise it for us.
        self._server_start_task.result()

        saml_url = f"{self.idp_url}{urllib.parse.quote_plus(saml_challenges[0].body)}"
        logger.info(
            f"Attempting to open browser. "
            f"Running a headless client? "
            f"You'll need to open this link in a browser: {saml_url}"
        )
        webbrowser.open(saml_url)

        # Wait for all SAML challenges to be handled by the listener
        await self.all_saml_challenges_handled.wait()

    async def handle(self, modeller_mailbox: _ModellerMailbox) -> None:
        try:
            # SAML is in use, so we are expecting SAML challenges from the pods
            saml_challenges = await modeller_mailbox.get_saml_challenges()

            # Process the SAML challenges & respond to them
            await self._handle_saml_challenges(
                modeller_mailbox.send_saml_responses,
                saml_challenges,
                modeller_mailbox.worker_mailboxes,
            )
        finally:
            await self.stop_server()

    async def stop_server(self) -> None:
        """Stop the web server."""
        await self.runner.cleanup()
