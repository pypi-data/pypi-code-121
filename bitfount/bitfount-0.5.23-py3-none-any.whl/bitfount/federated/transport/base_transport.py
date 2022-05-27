"""Base mailbox classes for other mailbox classes to inherit from."""
import asyncio
from asyncio import CancelledError, Task
from dataclasses import dataclass
import inspect
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    Mapping,
    Optional,
    TypeVar,
    Union,
    cast,
)

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from grpc import RpcError, StatusCode
import msgpack

from bitfount.federated.exceptions import (
    MessageHandlerNotFoundError,
    MessageRetrievalError,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
    _MessageEncryption,
    _MessageService,
    msgpackext_decode,
    msgpackext_encode,
)

SyncHandler = Callable[[_BitfountMessage], None]
AsyncHandler = Callable[[_BitfountMessage], Awaitable[None]]
Handler = Union[SyncHandler, AsyncHandler]

HANDLER_BACKOFF_SECONDS: int = 30


logger = _get_federated_logger(__name__)


class _BaseMailbox:
    """The base mailbox class.

    Contains handlers and message service.

    Args:
        mailbox_id: the ID of the mailbox to monitor.
        message_service: underlying message service instance.
        handlers: an optional mapping of message types to handlers to initialise with.
    """

    def __init__(
        self,
        mailbox_id: str,
        message_service: _MessageService,
        handlers: Optional[Mapping[_BitfountMessageType, Handler]] = None,
    ):
        self.mailbox_id = mailbox_id
        self.message_service = message_service

        self._handlers: Dict[_BitfountMessageType, Handler] = {}
        if handlers:
            # Register supplied handlers
            for message_type, handler in handlers.items():
                self.register_handler(message_type, handler)

        # Create a set of asyncio.Locks(), one for each message type. This enables
        # us to ensure that a single handler is running for a given message type
        # at a given time.
        # TODO: [BIT-1048] Revisit this and decide if _all_ messages need to be
        #       exclusive in this way.
        self._message_locks: Dict[_BitfountMessageType, asyncio.Lock] = {
            m_type: asyncio.Lock() for m_type in _BitfountMessageType
        }

        # Only one call to listen_for_messages() should be allowed at a time.
        # Otherwise we run the risk of messages being pulled off of the mailbox
        # by a listener that doesn't have the right handlers. Each mailbox should
        # only need one listener as it runs indefinitely.
        self._listening_lock = asyncio.Lock()

        # To enable a smart back-off when no handler is found before reattempting
        # we introduce an event that can monitor when new handlers are added. This
        # allows us to handle the situation where a response comes through faster
        # than the correct handler can be attached.
        self._new_handler_added = asyncio.Event()

    async def log(self, message: Mapping[str, object]) -> None:
        """Log message to remote task participant."""
        raise NotImplementedError

    def _setup_federated_logging(self) -> None:
        """Sets up federated logging."""
        raise NotImplementedError

    async def listen_for_messages(self) -> None:
        """Listens for messages on the target mailbox.

        Received messages are passed to the relevant handlers. If no relevant
        handlers are found, it will wait for up to `HANDLER_BACKOFF_SECONDS`
        for one to be registered. This avoids the situation of a response coming
        through faster than a handler can be registered. If not, it is passed
        to the default handler.
        """
        # Guarantee that only one listener is listening at a time.
        async with self._listening_lock:
            try:
                async for message in self.message_service.poll_for_messages(
                    self.mailbox_id
                ):
                    try:
                        await self._handle_message(message)
                    except MessageHandlerNotFoundError:
                        self._default_handler(message)
            # General message service issues to log out before failing.
            except RpcError as err:
                if err.code() == StatusCode.UNAVAILABLE:
                    logger.warning("Message Service unavailable")
                if err.code() == StatusCode.UNAUTHENTICATED:
                    # This could be a temporary token expiry issue
                    logger.info(
                        f"Authentication to read from '{self.mailbox_id}' failed"
                    )
                if err.code() == StatusCode.PERMISSION_DENIED:
                    logger.warning(
                        f"You don't own a pod with the mailbox: {self.mailbox_id}. "
                        f"Ensure it exists on Bitfount Hub."
                    )
                if err.code() == StatusCode.FAILED_PRECONDITION:
                    logger.debug(
                        f"No mailbox exists for '{self.mailbox_id}', "
                        f"ensure connect_pod() or send_task_requests() is called first."
                    )
                raise MessageRetrievalError(
                    f"An error occurred when trying to communicate"
                    f" with the messaging service: {err}"
                )

    async def _handle_message(self, message: _BitfountMessage) -> Task:
        """Finds and runs a handler for the supplied message.

        The handler (whether async or not) is run as an asyncio.Task to avoid
        blocking listen_for_messages().

        Args:
            message: The message to handle.

        Returns:
            The created asyncio.Task in which the handler is being run.

        Raises:
            MessageHandlerNotFoundError: If no handler is registered for message
                                         type and one is not registered within
                                         the timeout.
        """
        message_type: _BitfountMessageType = message.message_type

        # Try to find relevant handler for this message type
        handler: Handler = await self._retrieve_handler(message_type)

        # We create an async wrapper around the handler call regardless of if it's
        # an async function or not to allow us to run it in the background as a Task.
        # This also allows us to access the asyncio.Locks
        async def _running_handler_wrapper() -> None:
            # Only a single handler (i.e. the single handle function call) should
            # be running for a given message type at a given time; this helps avoid
            # conflicting use of shared resources and ensures that tasks we _want_
            # to block (such as worker running) do so.
            # TODO: [BIT-1048] Revisit this and decide if _all_ messages need to
            #       be exclusive in this way.
            async with self._message_locks[message_type]:
                # As this supports both sync and async handlers we need to
                # process the result (which should be None, but could be a
                # Coroutine returning None). As such, we comfortably call the
                # handler and then simply await the result if needed.
                result = handler(message)
                if inspect.isawaitable(result):
                    # Mypy needs some assurance, despite the above check
                    result = cast(Awaitable[None], result)
                    await result

        return asyncio.create_task(_running_handler_wrapper())

    async def _retrieve_handler(
        self, message_type: _BitfountMessageType, timeout: int = HANDLER_BACKOFF_SECONDS
    ) -> Handler:
        """Retrieve the registered handler for the given message type.

        If no handler is registered for message type, wait for up to `timeout`
        for one to be registered. Otherwise, raise KeyError.

        Args:
            message_type: Message type to retrieve handler for.
            timeout: Number of seconds to wait before declaring no handler found.

        Returns:
            The handler registered for the given message type.

        Raises:
            MessageHandlerNotFoundError: If no handler is registered for message
                                         type and one is not registered within
                                         the timeout.
        """
        # If handler is already registered, `_retrieve_handler_backoff()` will
        # return it immediately. Otherwise, we wait for it to return for at most
        # `timeout` seconds before raising KeyError.
        try:
            handler = await asyncio.wait_for(
                self._retrieve_handler_backoff(message_type),
                timeout=timeout,
            )
            return handler
        except asyncio.TimeoutError as te:
            # This is only for debug purposes as the KeyError will be swallowed
            # by the checks in listen_for_messages and the default handler will
            # be used to process the message.
            logger.debug(
                f"No handler found within backoff period "
                f"for message type {message_type}."
            )
            raise MessageHandlerNotFoundError from te

    async def _retrieve_handler_backoff(
        self, message_type: _BitfountMessageType
    ) -> Handler:
        """Wait for handler to be available for message type and return it."""
        # Loop indefinitely, waiting on handlers registration events.
        while True:
            await self._new_handler_added.wait()
            try:
                return self._handlers[message_type]
            except KeyError:
                # Clear the handler registration event so we can monitor when another
                # handler is registered.
                #
                # We do this at the end of the iteration so that we avoid a race
                # condition between when `_retrieve_handler_backoff()` is called
                # and when it is run where a handler could be registered in that
                # gap. Clearing the event at the start of the iteration would mean
                # that handler was missed.
                #
                # If it's not actually a "new" handler that caused the event to be
                # set, this is not an issue as the try...catch will handle it.
                self._new_handler_added.clear()

    def register_handler(
        self, message_type: _BitfountMessageType, handler: Handler
    ) -> None:
        """Registers a handler for a specific message type."""
        logger.debug(f"Registering handler {handler} for message type {message_type}")
        self._handlers[message_type] = handler

        # Note we've added a new handler, to allow backed off handler retrieval
        # to know.
        self._new_handler_added.set()

    def register_temp_handler(
        self, message_type: _BitfountMessageType, handler: Handler
    ) -> None:
        """Registers a handler that will be deleted after it is called."""
        logger.debug(
            f"Registering temporary handler {handler} for message type {message_type}"
        )
        self.register_handler(
            message_type, self._temp_handler_wrapper(message_type, handler)
        )

    def _temp_handler_wrapper(
        self, message_type: _BitfountMessageType, handler: Handler
    ) -> Handler:
        """Wraps handler so that it will be deleted after it is called."""

        def wrapped(message: _BitfountMessage) -> Any:
            result = handler(message)
            self.delete_handler(message_type)
            return result

        return wrapped

    def delete_handler(self, message_type: _BitfountMessageType) -> None:
        """Deletes the handler associated with the message type."""
        logger.debug(f"Deleting handler for message type: {message_type}")
        self._handlers.pop(message_type, None)  # avoids KeyError

    @staticmethod
    def _default_handler(message: _BitfountMessage) -> None:
        """Simple default handler that logs the message details.

        If this is called it is because we have received a message type that we
        were not expecting and do not know how to handle. We log out pertinent
        (non-private) details.
        """
        logger.error(
            f"Received unexpected message "
            f"("
            f"type: {message.message_type}; "
            f"sender {message.sender}; "
            f"recipient {message.recipient}"
            f"). "
            f"Message was not handled."
        )


@dataclass
class _WorkerMailboxDetails:
    """Mailbox details for a specific task/worker on a pod.

    Attributes:
        pod_identifier: The parent pod's identifier.
        public_key: The parent pod's public key.
        mailbox_id: The mailbox ID for this specific task/worker.
        aes_encryption_key: The encryption key to use for this specific task/worker.
    """

    pod_identifier: str
    public_key: RSAPublicKey
    mailbox_id: str
    aes_encryption_key: bytes


# Type variable for return type below.
R = TypeVar("R")


async def _send_aes_encrypted_message(
    message: Any,
    aes_encryption_key: bytes,
    message_service: _MessageService,
    **kwargs: Any,
) -> None:
    """Packs message, encrypts it and sends it.

    Args:
        message: The message to be sent. Must support serialisation via msgpack.
        aes_encryption_key: Key used to encrypt message.
        message_service: The MessageService used to send the message.
        **kwargs: Keyword arguments passed to BitfountMessage constructor.
    """
    body = msgpack.dumps(message, default=msgpackext_encode)
    message_body = _MessageEncryption.encrypt_outgoing_message(body, aes_encryption_key)

    await message_service.send_message(
        _BitfountMessage(body=message_body, **kwargs),
        already_packed=True,
    )


def _decrypt_aes_message(message: _BitfountMessage, aes_encryption_key: bytes) -> Any:
    """Decrypt AES encrypted message.

    Args:
        message: Encrypted message to decrypt.
        aes_encryption_key: The AES key to use to decrypt.

    Returns:
        Decrypted message body.
    """
    body = _MessageEncryption.decrypt_incoming_message(message.body, aes_encryption_key)
    return msgpack.loads(body, ext_hook=msgpackext_decode)


async def _run_func_and_listen_to_mailbox(
    run_func: Coroutine[None, None, R],
    mailbox: _BaseMailbox,
) -> R:
    """Runs an async function and listens for messages simultaneously.

    This function allows any exceptions that occur in the run function or the
    listening method to be properly propagated to the calling code, which is not
    possible with a normal `asyncio.create_task()` wrapper.

    It also ensures that the mailbox.listen_for_messages() method is not run for
    longer than the lifetime of run_func.

    Args:
        run_func: The function to run that will be needing received messages.
        mailbox: The mailbox to use to listen for messages.

    Returns:
         The return value of run_func.
    """
    # Create a task for listening for messages. We do this first so the wrapper
    # can be aware of it.
    mailbox_listen_task: Task = asyncio.create_task(mailbox.listen_for_messages())

    # Create wrapper around function call so that it will cancel the mailbox
    # listening task once the run task is finished.
    async def run_func_wrapper() -> R:
        # Await the result of the provided coroutine.
        result = await run_func

        # As function is finished, cancel the mailbox from listening for messages.
        mailbox_listen_task.cancel()

        return result

    # Create a separate task for the wrapped function call
    run_task: Task = asyncio.create_task(run_func_wrapper())

    # Await on either the wrapped function call to finish (which will cause the
    # mailbox_listen_task to finish) or for one of them to throw an exception.
    # In that case we cancel both tasks (we won't know which one failed) and re-raise
    # the exception.
    try:
        await asyncio.gather(run_task, mailbox_listen_task, return_exceptions=False)
    except CancelledError:
        # This should be fine, and is likely just the mailbox_listen_task being
        # cancelled because the run task has finished, but we should log some info
        # out just in case.
        if run_task.cancelled():
            logger.debug("Run task was cancelled.")
        if mailbox_listen_task.cancelled():
            logger.debug("Mailbox listen_for_messages() task was cancelled.")
    except BaseException as ex:
        # This exception is re-raised down below, so it doesn't matter that this
        # clause is very broad. We want to capture even BaseExceptions to ensure
        # that we cancel the other task.
        if not isinstance(ex, asyncio.TimeoutError):
            logger.error("Exception encountered whilst waiting for run function")
            logger.exception(ex)
        else:
            # A TimeoutError is expected in the normal course of things so we don't
            # want to log it out. It is handled up the chain by the Pod before returning
            # to a graceful state. However we still want to cancel any associated tasks.
            logger.debug("TimeoutError encountered whilst waiting for run function")

        # Pass the exception into the other task so it can be notified
        other_task: Optional[Task] = None
        if not run_task.done():
            other_task = run_task
        elif not mailbox_listen_task.done():
            other_task = mailbox_listen_task

        if other_task:
            try:
                coro = other_task.get_coro()
                try:
                    # Assume that coro is a coroutine rather than an awaitable
                    coro = cast(Coroutine, coro)
                    coro.throw(ex)
                except AttributeError:
                    logger.warning(f"Unable to `throw()` exception into coro {coro}")
            except StopIteration:
                pass

        # Cancel both tasks if they're still running
        for task in [run_task, mailbox_listen_task]:
            try:
                task.cancel()
            except CancelledError:
                pass

        # Re-raise the initial exception
        raise ex

    # If no exceptions were thrown, return the result of the wrapped function call.
    run_result: R = run_task.result()
    return run_result
