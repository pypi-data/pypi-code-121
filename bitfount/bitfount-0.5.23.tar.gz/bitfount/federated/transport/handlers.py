"""Callbacks and wrappers for async message service calls."""
from __future__ import annotations

import asyncio
from collections.abc import Iterable
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Collection,
    Generic,
    Optional,
    Set,
    TypeVar,
    Union,
    cast,
)

if TYPE_CHECKING:
    from bitfount.federated.transport.base_transport import _BaseMailbox, Handler
    from bitfount.federated.transport.message_service import (
        _BitfountMessage,
        _BitfountMessageType,
    )

from bitfount.federated.logging import _get_federated_logger

logger = _get_federated_logger(__name__)
R = TypeVar("R")


class _AsyncCallback(Generic[R]):
    """Async wrapper around a callback function.

    Allows us to `await` on the result of this callback. By overriding __call__
    the fact that we've wrapped the callback is transparent to the calling code.
    """

    def __init__(self, fn: Callable[[_BitfountMessage], R]):
        """Create a new AsyncCallback.

        Args:
            fn: the callback function to be wrapped.
        """
        self._fn = fn
        self._result_exists = asyncio.Event()
        self._result: R

    def __call__(self, message: _BitfountMessage) -> None:
        """Call the underlying (synchronous) callback function."""
        # Overriding __call__ allows us to transparently wrap the underlying
        # function call so that the call to the async callback looks just like
        # a normal call to the function itself.
        self._result = self._fn(message)
        self._result_exists.set()

    async def result(self, timeout: Optional[int] = None) -> R:
        """Asynchronously retrieve the result of the callback.

        Will (non-blockingly) wait on the callback to be called.

        Args:
            timeout: Timeout in seconds to await on the result. If not
                provided, will wait indefinitely. Optional.

        Returns:
            The return value of the callback.

        Raises:
            asyncio.TimeoutError: If timeout provided and result is not set within
                timeout seconds.
        """
        if timeout:
            await asyncio.wait_for(self._result_exists.wait(), timeout)
        else:
            await self._result_exists.wait()
        return self._result

    def reset(self) -> None:
        """Clears the result of the callback, allowing it to be re-used."""
        # We don't need to clear the actual result here as that's set before the
        # _result_exists is set.
        self._result_exists.clear()


def _simple_message_returner(x: _BitfountMessage) -> _BitfountMessage:
    """Simple callback that simply returns the message."""
    return x


def _get_message_awaitable() -> _AsyncCallback[_BitfountMessage]:
    """Returns an awaitable wrapper around message retrieval."""
    return _AsyncCallback(_simple_message_returner)


class _AsyncMultipleResponsesHandler:
    """Wraps multiple expected responses in a singular awaitable."""

    def __init__(
        self,
        handler: Handler,
        message_types: Union[_BitfountMessageType, Collection[_BitfountMessageType]],
        mailbox: _BaseMailbox,
        responders: Collection[str],
    ):
        """Creates a handler for multiple responses of a given type(s).

        When expecting multiple separate responses from a set of responders, this
        class will provide an awaitable that returns when either all expected responses
        have been received, or when a timeout is reached (in which case it returns
        the set of those who didn't respond).

        Each message is passed to the assigned handler and track is kept of those
        who have responded. The awaitable returned blocks asynchronously on all
        responses being received.

        Can be used as a context manager which ensures that all message type handlers
        are correctly attached and removed at the end of the usage.

        Args:
            handler: The async function to call for each received message.
            message_types: The message types to handle.
            mailbox: The mailbox where messages will be received.
            responders: The set of expected responders.
        """
        self._orig_handler = handler
        if not isinstance(message_types, Iterable):
            message_types = [message_types]
        self._message_types = message_types
        self._mailbox = mailbox
        self.responders = responders

        # Initialise to the full set of expected and remove them as they response.
        self._not_responded = set(responders)

        # Synchronization primitives for handling multiple responses coming in
        # simultaneously and for keeping track of when all responses have been received.
        self._lock = asyncio.Lock()
        self._responses_done = asyncio.Event()
        self._timeout_reached = False

    async def handler(self, message: _BitfountMessage) -> None:
        """An augmented handler for multiple responses.

        Wraps the supplied handler and tracks the expected responses.

        Args:
            message: The message to be processed.
        """
        # We want to wrap the supplied handler with additional logic to (a) avoid
        # multiple calls to the handler simultaneously which may mess with state,
        # and (b) to enable us to monitor when all responses have been received so
        # we can exit.

        # This lock prevents multiple calls to the handler at the same time
        async with self._lock:
            # This check prevents calls being processed after we have marked it
            # as done, for instance if timeout has occurred.
            if not self._responses_done.is_set():
                # We mark the responder as responded and handle cases where we
                # receive an unexpected response.
                try:
                    self._not_responded.remove(message.sender)
                except KeyError:
                    if message.sender in self.responders:
                        logger.error(
                            f"Received multiple responses from {message.sender}; "
                            f"only expecting one response per responder."
                        )
                    else:
                        logger.error(
                            f"Received unexpected response from {message.sender}; "
                            f"they were not in the list of expected responders."
                        )
                # Once marked as responded we can call the underlying handler and then
                # check whether all responses have been received.
                else:
                    # As this supports both sync and async handlers we need to
                    # process the result (which should be None, but could be a
                    # Coroutine returning None). As such, we comfortably call the
                    # handler and then simply await the result if needed.
                    handler_return = self._orig_handler(message)
                    if inspect.isawaitable(handler_return):
                        # Mypy needs some assurance, despite the above check
                        handler_return = cast(Awaitable[None], handler_return)
                        await handler_return

                    if len(self._not_responded) == 0:
                        self._responses_done.set()
            # Handle responses received after we're marked as done
            else:
                if self._timeout_reached:
                    logger.warning(
                        f"Message received after timeout reached; "
                        f"responder too slow, message will not be processed: {message}"
                    )
                else:
                    logger.warning(
                        f"Received unexpected message after all responses were "
                        f"accounted for: {message}"
                    )

    def __enter__(self) -> _AsyncMultipleResponsesHandler:
        self.setup_handlers()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.remove_handlers()

    def setup_handlers(self) -> None:
        """Setup the augmented handler for the supplied message types."""
        for message_type in self._message_types:
            self._mailbox.register_handler(message_type, self.handler)

    def remove_handlers(self) -> None:
        """Remove the augmented handler for the supplied message types."""
        for message_type in self._message_types:
            self._mailbox.delete_handler(message_type)

    async def wait_for_responses(self, timeout: Optional[int] = None) -> Set[str]:
        """Waits for the set of responses to be handled.

        Each response is passed to the supplied (augmented) handler and this method
        will return once all responders have responded or until timeout is reached.

        Args:
            timeout: Optional. Timeout in seconds to wait for all responses to be
                received. If provided, any responders who failed to respond in time
                will be returned as a set.

        Returns:
            The set of responders who did not respond in time.
        """
        # Wait for all responses to have been received or
        # until the timeout expires (if provided).
        try:
            if timeout:
                await asyncio.wait_for(self._responses_done.wait(), timeout)
            else:
                await self._responses_done.wait()
        except asyncio.TimeoutError:
            self._timeout_reached = True
            # Acquiring the lock guarantees that no other responses are
            # _currently_ being processed (and hence we can set the event)
            async with self._lock:
                # Setting this stops other responses in the event loop from
                # being processed _later_.
                self._responses_done.set()

        # Will be empty if all responses received
        return self._not_responded
