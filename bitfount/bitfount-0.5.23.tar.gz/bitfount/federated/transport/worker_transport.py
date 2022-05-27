"""Handles messages for a Pods and Modellers at the protocol level during a task."""
import asyncio
import logging
from typing import Any, Callable, Dict, Final, Iterable, List, Mapping, Optional

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import msgpack

from bitfount.federated.encryption import _RSAEncryption
from bitfount.federated.logging import _federate_logger, _get_federated_logger
from bitfount.federated.transport.base_transport import (
    Handler,
    _BaseMailbox,
    _send_aes_encrypted_message,
)
from bitfount.federated.transport.handlers import (
    _AsyncMultipleResponsesHandler,
    _get_message_awaitable,
)
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
    _DecryptedBitfountMessage,
    _MessageService,
)
from bitfount.federated.transport.types import (
    _OIDCAuthFlowResponse,
    _OIDCClientID,
    _PodDeviceCodeDetails,
)
from bitfount.federated.types import _PodResponseType
from bitfount.types import _JSONDict, _SAMLResponse, _SerializedWeights

logger = _get_federated_logger(__name__)

# How long to wait for Modeller authentication response
_DEFAULT_AUTHENTICATION_MODELLER_RESPONSE_TIMEOUT: Final[int] = 5 * 60  # 5 minutes
# How long to wait for a response from the modeller before checking if the modeller is
# still online.
_SOFT_LIMIT_MESSAGE_TIMEOUT: Final[int] = 30  # seconds
# How long to wait for a response from the modeller regarding their online status before
# aborting the task. The hard limit can only be reached after the soft limit has already
# been reached.
_HARD_LIMIT_MESSAGE_TIMEOUT: Final[int] = 30  # seconds


class _WorkerMailbox(_BaseMailbox):
    """Used by a pod for handling messages during a task."""

    def __init__(
        self,
        pod_identifier: str,
        modeller_mailbox_id: str,
        modeller_name: str,
        aes_encryption_key: bytes,
        message_service: _MessageService,
        pod_mailbox_ids: Mapping[str, str],
        handlers: Optional[Mapping[_BitfountMessageType, Handler]] = None,
    ):
        """Create new worker mailbox for a specific task.

        Args:
            pod_identifier: identifier for the pod that contains this worker.
            modeller_mailbox_id: mailbox id for modeller involved in the task.
            modeller_name: name of the modeller involved in the task.
            aes_encryption_key: encryption key for task messages.
            message_service: the underlying message service.
            pod_mailbox_ids: mapping of pod_identifier to worker mailbox IDs for
                             all pods involved in the task.
            handlers: an optional mapping of message types to handlers to initialise
                      with.
        """
        # Our own mailbox ID is stored in the pods mailbox dict.
        super().__init__(
            mailbox_id=pod_mailbox_ids[pod_identifier],
            message_service=message_service,
            handlers=handlers,
        )
        self.pod_identifier = pod_identifier
        self.modeller_mailbox_id = modeller_mailbox_id
        self.modeller_name = modeller_name
        self.aes_encryption_key = aes_encryption_key
        self.pod_mailbox_ids: Dict[str, str] = dict(pod_mailbox_ids)

        # Gather list of other pods. Iteration order is important here (to ensure
        # consistency between share generation order), so we use List rather than
        # another collection.
        self.other_pods: List[str] = [
            pod_identifier
            for pod_identifier in pod_mailbox_ids
            if pod_identifier != self.pod_identifier
        ]

        self._setup_federated_logging()

    async def accept_task(self) -> None:
        """Sends an acceptance message to the modeller."""
        await self._send_aes_encrypted_message(
            {_PodResponseType.ACCEPT.name: self.pod_identifier},
            _BitfountMessageType.JOB_ACCEPT,
        )

    async def reject_task(
        self,
        error_messages: Mapping[str, Iterable[str]],
    ) -> None:
        """Send a rejection of a training request to a modeller.

        Args:
            error_messages: Error messages to send

        Returns:
            True if message sent successfully, else false

        """
        logger.info(f"Rejecting task from {self.modeller_name}")
        logger.debug(
            f"Rejected task from {self.modeller_name} "
            f"at mailbox: {self.modeller_mailbox_id}"
        )
        await self._send_aes_encrypted_message(
            error_messages, _BitfountMessageType.JOB_REJECT
        )

    async def issue_saml_challenge(
        self,
        saml_request: str,
    ) -> None:
        """Send SAML challenge to a modeller."""
        logger.info(f"Issuing SAML Challenge to: '{self.modeller_name}'.")
        await self._send_aes_encrypted_message(
            saml_request, _BitfountMessageType.SAML_REQUEST
        )

    async def get_saml_response(
        self, timeout: Optional[int] = _DEFAULT_AUTHENTICATION_MODELLER_RESPONSE_TIMEOUT
    ) -> _SAMLResponse:
        """Awaits for the SAML Response from the modeller."""
        saml_response: _SAMLResponse = await self._get_message_and_decrypt(
            _BitfountMessageType.SAML_RESPONSE, timeout
        )
        return saml_response

    async def send_oidc_client_id(self, client_id: str) -> None:
        """Sends the Client ID to use for OIDC authentication to modeller."""
        logger.info("Sending client ID to modeller for OIDC authentication.")
        await self._send_aes_encrypted_message(
            _OIDCClientID(client_id).serialize(),
            _BitfountMessageType.OIDC_CHALLENGE,
        )

    async def get_oidc_auth_flow_response(
        self, timeout: Optional[int] = _DEFAULT_AUTHENTICATION_MODELLER_RESPONSE_TIMEOUT
    ) -> _OIDCAuthFlowResponse:
        """Get OIDC Auth Code Flow response from the modeller.

        Response will contain an authorization code, code verifier, and redirect URI.

        Args:
            timeout: How long to wait for response, in seconds. If `None`, will wait
                indefinitely. Defaults to 5 minutes.

        Returns:
            Tuple of authorization code, code verifier, and redirect URI.
        """
        logger.info(f"Awaiting OIDC response from '{self.modeller_name}'")
        decrypted: _JSONDict = await self._get_message_and_decrypt(
            _BitfountMessageType.OIDC_AFC_PKCE_RESPONSE, timeout
        )

        # Check contents
        try:
            return _OIDCAuthFlowResponse.deserialize(decrypted)
        except (KeyError, TypeError):
            try:
                # Assume it's a dict but that we just couldn't deserialize it
                raise KeyError(
                    f"Expected auth_code, code_verifier, and redirect_uri to be in "
                    f"OIDC response; got {decrypted.keys()}"
                )
            except AttributeError:
                # If not, raise a TypeError
                raise TypeError(
                    f"Unable to access OIDC response contents; expected dict, "
                    f"got {type(decrypted)}"
                )

    async def get_oidc_device_code_response(
        self, timeout: Optional[int] = _DEFAULT_AUTHENTICATION_MODELLER_RESPONSE_TIMEOUT
    ) -> _PodDeviceCodeDetails:
        """Get OIDC Device Code Flow response from the modeller.

        Response will contain a device code, and polling details.

        Args:
            timeout: How long to wait for response, in seconds. If `None`, will wait
                indefinitely. Defaults to 5 minutes.

        Returns:
            Tuple device code, when the code expires, and the polling interval to use.
        """
        logger.info(f"Awaiting OIDC device response from '{self.modeller_name}'")
        decrypted: _JSONDict = await self._get_message_and_decrypt(
            _BitfountMessageType.OIDC_DEVICE_CODE_RESPONSE, timeout
        )

        # Check contents and decode as needed
        try:
            return _PodDeviceCodeDetails.deserialize(decrypted)
        except (KeyError, TypeError):
            try:
                # Assume it's a dict but that we just couldn't deserialize it
                raise KeyError(
                    f"Expected device_code, expires_at, and interval to be in "
                    f"OIDC response; got {decrypted.keys()}"
                )
            except AttributeError:
                # If not, raise a TypeError
                raise TypeError(
                    f"Unable to access OIDC response contents; expected dict, "
                    f"got {type(decrypted)}"
                )

    async def _send_aes_encrypted_message(
        self, object_to_send: Any, message_type: _BitfountMessageType
    ) -> None:
        """Send message to modeller, AES encrypted.

        Args:
            object_to_send: Body of the message (not encrypted)
            message_type: The type of the message to send
        """
        await _send_aes_encrypted_message(
            object_to_send,
            self.aes_encryption_key,
            self.message_service,
            message_type=message_type,
            recipient=self.modeller_name,
            recipient_mailbox_id=self.modeller_mailbox_id,
            sender=self.pod_identifier,
            sender_mailbox_id=self.mailbox_id,
        )

    async def send_evaluation_results(self, eval_results: Mapping[str, float]) -> None:
        """Sends evaluation results to the modeller."""
        await self._send_aes_encrypted_message(
            eval_results, _BitfountMessageType.EVALUATION_RESULTS
        )

    async def _get_message(
        self, message_type: _BitfountMessageType, timeout: Optional[int]
    ) -> _BitfountMessage:
        """Generic handler for single message retrieval.

        Args:
            message_type: The type of message to wait on.
            timeout: How long to wait before timing out.

        Returns:
            The message.

        Raises:
            asyncio.TimeoutError: If the message is not received within the timeout.
        """
        # Registers the handler for the expected message type
        async_awaitable = _get_message_awaitable()
        self.register_temp_handler(message_type, async_awaitable)

        # Waits for the message until a `TimeoutError` occurs. If a message is received
        # before the timeout, it is simply returned. Otherwise, a message is sent to the
        # modeller to check that they are still online. If they are online, the timeout
        # resets and we wait for the original message again. If they are not online,
        # this will raise another `TimeoutError` waiting for the Modeller's response. On
        # the second timeout, the task is cancelled by sending a `TASK_ABORT` message to
        # the modeller and re-raising the original `TimeoutError`.
        while True:
            try:
                message = await async_awaitable.result(timeout)
                break
            except asyncio.TimeoutError as te:
                logger.debug(
                    f"Soft limit timeout hit waiting for message {message_type.name}."
                )
                modeller_status_async_awaitable = _get_message_awaitable()
                self.register_temp_handler(
                    _BitfountMessageType.ONLINE_RESPONSE,
                    modeller_status_async_awaitable,
                )
                logger.info("Checking if Modeller is still online...")
                await self.check_modeller_online()

                try:
                    await modeller_status_async_awaitable.result(
                        _HARD_LIMIT_MESSAGE_TIMEOUT
                    )
                    logger.info("Modeller is online.")
                except asyncio.TimeoutError:
                    logger.warning("Modeller is offline. Aborting task.")
                    await self.send_task_abort_message()
                    raise te

        return message

    def _aes_decrypt(self, message: _BitfountMessage) -> Any:
        """Decrypt message from modeller.

        Args:
            message: Encrypted message to decrypt.

        Returns:
            Decrypted message body.
        """
        return message.decrypt(self.aes_encryption_key).body

    async def _get_message_and_decrypt(
        self,
        message_type: _BitfountMessageType,
        timeout: Optional[int] = _SOFT_LIMIT_MESSAGE_TIMEOUT,
    ) -> Any:
        """Generic handler for single encrypted message retrieval.

        Args:
            message_type: The type of message to wait on.
            timeout: How long to wait before timing out.

        Returns:
            The decrypted message contents.
        """
        message = await self._get_message(message_type, timeout)
        return self._aes_decrypt(message)

    async def get_training_iteration_complete_update(
        self, timeout: Optional[int] = _SOFT_LIMIT_MESSAGE_TIMEOUT
    ) -> bool:
        """Awaits for the next training complete update from the modeller."""
        training_complete: bool = await self._get_message_and_decrypt(
            _BitfountMessageType.TRAINING_COMPLETE, timeout=timeout
        )
        return training_complete

    async def get_task_complete_update(
        self, timeout: Optional[int] = _SOFT_LIMIT_MESSAGE_TIMEOUT
    ) -> None:
        """Awaits for the task complete message from the modeller."""
        await self._get_message_and_decrypt(
            _BitfountMessageType.TASK_COMPLETE, timeout=timeout
        )

    async def check_modeller_online(self) -> None:
        """Send message to Modeller to check if the Modeller is online."""
        await self._send_aes_encrypted_message(None, _BitfountMessageType.ONLINE_CHECK)

    async def send_task_abort_message(self) -> None:
        """Send task abort message to Modeller."""
        await self._send_aes_encrypted_message(None, _BitfountMessageType.TASK_ABORT)

    async def log(self, message: Mapping[str, object]) -> None:
        """Log message to Modeller."""
        await self._send_aes_encrypted_message(
            message, _BitfountMessageType.LOG_MESSAGE
        )

    def _setup_federated_logging(self) -> None:
        """Set up federated logging."""
        _federate_logger(self)

        def log_message_handler(message: _BitfountMessage) -> None:
            log_message: _JSONDict = self._aes_decrypt(message)
            # We prepend the log message to show it's come from the Modeller
            log_message["msg"] = f"Modeller: {log_message['msg']}"
            # We remove the `federated` key to avoid recursively sending a federated
            # log message on both the Modeller and Worker sides
            log_message.pop("federated")
            logger.handle(logging.makeLogRecord(log_message))

        self.register_handler(_BitfountMessageType.LOG_MESSAGE, log_message_handler)


async def _send_training_metrics(
    validation_metrics: Mapping[str, str],
    worker_mailbox: _WorkerMailbox,
) -> None:
    """Sends a model parameter update to the modeller.

    Args:
        validation_metrics: The relevant metrics at training iteration.
        worker_mailbox: The worker mailbox to use to send the parameter update.
    """
    # Deliberate access to private method here as that method shouldn't be used in
    # any other context than transport layer access.
    # noinspection PyProtectedMember
    await worker_mailbox._send_aes_encrypted_message(
        validation_metrics, _BitfountMessageType.TRAINING_METRICS
    )


async def _send_parameter_update(
    parameter_update: _SerializedWeights, worker_mailbox: _WorkerMailbox
) -> None:
    """Sends a model parameter update to the modeller.

    Args:
        parameter_update: The parameter update to send, already serialized.
        worker_mailbox: The worker mailbox to use to send the parameter update.
    """
    # Deliberate access to private method here as that method shouldn't be used in
    # any other context than transport layer access.
    # noinspection PyProtectedMember
    await worker_mailbox._send_aes_encrypted_message(
        parameter_update, _BitfountMessageType.TRAINING_UPDATE
    )


async def _get_model_parameters(
    worker_mailbox: _WorkerMailbox, timeout: Optional[int] = _SOFT_LIMIT_MESSAGE_TIMEOUT
) -> _SerializedWeights:
    """Awaits for the next model parameter update from the modeller.

    Args:
        worker_mailbox: The worker mailbox that the message will be sent to.
        timeout: Optional. The time to wait in seconds for the next model
            parameter update.

    Returns:
        The received parameter update.
    """
    # Await messages for updates sent modeller->worker
    # Deliberate access to private method here as that method shouldn't be used in
    # any other context than transport layer access.
    # noinspection PyProtectedMember
    weights: _SerializedWeights = await worker_mailbox._get_message_and_decrypt(
        _BitfountMessageType.MODEL_PARAMETERS, timeout=timeout
    )

    return weights


class _InterPodWorkerMailbox(_WorkerMailbox):
    """A worker mailbox that also handles pod-to-pod communication.

    In particular ensures that other pod RSA keys are stored and used.
    """

    def __init__(
        self,
        pod_public_keys: Mapping[str, RSAPublicKey],
        private_key: RSAPrivateKey,
        *args: Any,
        **kwargs: Any,
    ):
        """Create new inter-pod worker mailbox for a specific task.

        Args:
            pod_public_keys: Mapping of pod_identifier to the pod's RSA public
                             key for all pods involved in the task. This is for
                             inter-pod communication.
            private_key: The RSA private key for this pod.
            *args: Positional arguments as per _WorkerMailbox.
            **kwargs: Keyword arguments as per _WorkerMailbox.
        """
        super().__init__(*args, **kwargs)
        self._pod_public_keys = pod_public_keys

        # Check that we have public keys for all other pods
        missing_keys = set(self.other_pods) - set(self._pod_public_keys.keys())
        if missing_keys:
            missing_keys_str = ", ".join(missing_keys)
            raise ValueError(
                f"We are missing public keys for the following pods: "
                f"{missing_keys_str}. "
                f"Unable to continue inter-pod communication."
            )

        self._private_key = private_key

    async def _send_pod_to_pod_message(
        self,
        recipient: str,
        recipient_mailbox_id: str,
        object_to_send: Any,
        message_type: _BitfountMessageType,
    ) -> None:
        """Send message to other pod/worker, unencrypted.

        Args:
            recipient: The identifier of the worker/pod.
            recipient_mailbox_id: The mailbox to send message to.
            object_to_send: Body of the message (not encrypted).
            message_type: The type of the message to send.
        """
        try:
            recipient_key = self._pod_public_keys[recipient]
        except KeyError:
            logging.error(
                f"Unable to find public key for pod {recipient}. "
                f"Unable to send pod-to-pod message."
            )
            return None

        message_body: bytes = _RSAEncryption.encrypt(
            msgpack.dumps(object_to_send), recipient_key
        )
        await self.message_service.send_message(
            _BitfountMessage(
                message_type=message_type,
                body=message_body,
                recipient=recipient,
                recipient_mailbox_id=recipient_mailbox_id,
                sender=self.pod_identifier,
                sender_mailbox_id=self.mailbox_id,
            ),
            already_packed=True,
        )

    def _pod_to_pod_message_handler(
        self, message: _BitfountMessage
    ) -> _DecryptedBitfountMessage:
        """Handler for decrypting pod-to-pod messages."""
        return message.decrypt_rsa(self._private_key)


async def _send_secure_shares_to_others(
    secure_share_generator: Callable[[], int],
    worker_mailbox: _InterPodWorkerMailbox,
) -> None:
    """Sends result of `secure_share_generator` to all other pods in training task.

    Args:
        secure_share_generator: The function to be called which returns
                                the secure share to be sent.
        worker_mailbox: The worker mailbox to send the shares with.
    """
    for worker_identifier in worker_mailbox.other_pods:
        worker_mailbox_id = worker_mailbox.pod_mailbox_ids[worker_identifier]

        logger.debug(
            f"Sending secure share to mailbox of other worker "
            f"(from {worker_mailbox.pod_identifier} to {worker_identifier}): "
            f"{worker_mailbox_id}"
        )

        share = secure_share_generator()
        # Deliberate access to private method here as that method shouldn't be used in
        # any other context than transport layer access.
        # noinspection PyProtectedMember
        await worker_mailbox._send_pod_to_pod_message(
            recipient=worker_identifier,
            recipient_mailbox_id=worker_mailbox_id,
            object_to_send=share,
            message_type=_BitfountMessageType.SECURE_SHARE,
        )


async def _get_worker_secure_shares(
    worker_mailbox: _InterPodWorkerMailbox, timeout: Optional[int] = None
) -> List[int]:
    """Awaits the set of secure shares from the other workers.

    Args:
        worker_mailbox: The worker mailbox the shares will be received at.
        timeout: Optional. The number of seconds to wait for secure shares to arrive.

    Returns:
        The list of received shares.
    """
    shares: List[int] = []

    # Create light-weight handler to append to shared list.
    # Note that the secure shares are NOT received as encrypted messages.
    def worker_secure_share_handler(message: _BitfountMessage) -> None:
        logger.debug(f"Receiving secure share from worker {message.sender}")
        # Deliberate access to private method here as that method shouldn't be used in
        # any other context than transport layer access.
        # noinspection PyProtectedMember
        decrypted_message = worker_mailbox._pod_to_pod_message_handler(message)
        share: int = decrypted_message.body
        shares.append(share)

    # Await on all the other workers to send their shares, which will be
    # appended to the list above.
    with _AsyncMultipleResponsesHandler(
        handler=worker_secure_share_handler,
        message_types=_BitfountMessageType.SECURE_SHARE,
        mailbox=worker_mailbox,
        responders=worker_mailbox.other_pods,
    ) as response_handler:
        await response_handler.wait_for_responses(timeout=timeout)

    return shares
