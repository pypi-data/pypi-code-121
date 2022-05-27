"""Handles Modeller sending training requests and receiving pod responses."""
from __future__ import annotations

import logging
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    List,
    Mapping,
    MutableMapping,
    MutableSequence,
    Optional,
    Set,
    Tuple,
    cast,
)

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from grpc import RpcError

from bitfount.federated.encryption import _AESEncryption
from bitfount.federated.exceptions import BitfountTaskStartError
from bitfount.federated.logging import _federate_logger, _get_federated_logger
from bitfount.federated.transport.base_transport import (
    Handler,
    MessageRetrievalError,
    _BaseMailbox,
    _send_aes_encrypted_message,
    _WorkerMailboxDetails,
)
from bitfount.federated.transport.handlers import _AsyncMultipleResponsesHandler
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
from bitfount.federated.transport.utils import _average_training_metrics
from bitfount.federated.types import (
    _RESPONSE_MESSAGES,
    SerializedProtocol,
    _PodResponseType,
    _TaskRequestMessageGenerator,
)
from bitfount.types import _JSONDict, _SAMLResponse, _SerializedWeights

logger = _get_federated_logger(__name__)

_DEFAULT_TASK_RESPONSE_TIMEOUT: Final[int] = 5 * 60  # 5 minutes
_DEFAULT_OIDC_CLIENT_IDS_TIMEOUT: Final[int] = 5 * 60  # 5 minutes


class _ModellerMailbox(_BaseMailbox):
    """Handles message interactions with pods."""

    def __init__(
        self,
        mailbox_id: str,
        worker_mailboxes: Mapping[str, _WorkerMailboxDetails],
        message_service: _MessageService,
        handlers: Optional[Mapping[_BitfountMessageType, Handler]] = None,
    ):
        """Creates a new ModellerMailbox.

        Note that the preferred way to get a new ModellerMailbox is by calling
        ModellerMailbox.send_task_requests() which will instantiate the correct
        ModellerMailbox for you.

        Args:
            mailbox_id: The mailbox ID for this modeller mailbox.
            worker_mailboxes: A mapping of pod identifiers to worker mailbox details
                              for the pods/workers that will be involved in this task.
            message_service: The underlying message service.
            handlers: Optional. A set of handlers to initialise with.
        """
        super().__init__(
            mailbox_id=mailbox_id, message_service=message_service, handlers=handlers
        )
        self.worker_mailboxes: Dict[str, _WorkerMailboxDetails] = dict(worker_mailboxes)
        self._pod_identifiers: Set[str] = set(worker_mailboxes.keys())

        self.accepted_worker_mailboxes: Dict[str, _WorkerMailboxDetails] = {}

        self._setup_federated_logging()
        self._setup_online_status_handler()

    ############################
    # Task Setup Phase Methods #
    ############################
    @classmethod
    async def send_task_requests(
        cls,
        serialized_protocol: SerializedProtocol,
        pod_public_keys: Mapping[str, RSAPublicKey],
        task_request_msg_gen: _TaskRequestMessageGenerator,
        message_service: _MessageService,
    ) -> _ModellerMailbox:
        """Sends task requests, such as training requests, to pods.

        Appropriate mailboxes will be created for the modeller and worker mailboxes
        for the pods.

        Args:
            serialized_protocol: The serialized protocol to use for the task.
            pod_public_keys: A mapping of pod identifiers to their public keys for all
                the pods involved in this task request.
            task_request_msg_gen: A callable which will generate a task request message
                appropriate to the chosen verification method.
            message_service: The underlying message service to use.

        Returns:
            The created modeller mailbox for this task.
        """
        modeller_mailbox_id, worker_mailboxes = await cls._send_task_requests(
            serialized_protocol,
            pod_public_keys,
            task_request_msg_gen=task_request_msg_gen,
            message_service=message_service,
        )
        modeller_mailbox = cls(
            mailbox_id=modeller_mailbox_id,
            worker_mailboxes=worker_mailboxes,
            message_service=message_service,
        )
        return modeller_mailbox

    @classmethod
    async def _send_task_requests(
        cls,
        serialized_protocol: SerializedProtocol,
        pod_public_keys: Mapping[str, RSAPublicKey],
        task_request_msg_gen: _TaskRequestMessageGenerator,
        message_service: _MessageService,
    ) -> Tuple[str, Dict[str, _WorkerMailboxDetails]]:
        """Manage sending of task requests, such as training requests, to pods.

        Args:
            serialized_protocol: The serialized protocol to use for the task.
            pod_public_keys: A mapping of pod identifiers to their public keys for all
                the pods involved in this task request.
            task_request_msg_gen: A callable which will generate a task request message
                appropriate to the chosen verification method.
            message_service: The underlying message service to use.

        Returns:
            Tuple of:
                - (str) modeller mailbox ID
                - (dict) of pod identifier to worker mailbox details
        """
        # Shorthand the pod identifiers for ease of use
        pod_identifiers: List[str] = list(pod_public_keys)

        # Generate encryption keys and then task request messages for each pod.
        aes_key_per_pod = {
            pod_identifier: _AESEncryption.generate_key()
            for pod_identifier in pod_identifiers
        }
        task_request_per_pod: Dict[str, bytes] = {
            pod_identifier: task_request_msg_gen(
                serialized_protocol,
                pod_identifiers,
                aes_key_per_pod[pod_identifier],
                pod_public_key,
            )
            for pod_identifier, pod_public_key in pod_public_keys.items()
        }

        # Send this message to each pod and receive the modeller's mailbox ID
        # and the mailbox IDs of all the pods in the task.
        try:
            (
                modeller_mailbox_id,
                worker_mailbox_ids,
            ) = await message_service.setup_communication_with_pods(
                task_request_per_pod
            )
            logger.info(f"Sent task requests to {pod_identifiers}")
        except RpcError as err:
            logger.error(
                f"Failed to start task with pods: {pod_identifiers}. Error: {err}"
            )
            raise BitfountTaskStartError(
                f"Failed to start task with pods: {pod_identifiers}"
            )

        return (
            modeller_mailbox_id,
            {
                pod_identifier: _WorkerMailboxDetails(
                    pod_identifier,
                    pod_public_keys[pod_identifier],
                    worker_mailbox_id,
                    aes_key_per_pod[pod_identifier],
                )
                for pod_identifier, worker_mailbox_id in worker_mailbox_ids.items()
            },
        )

    async def get_oidc_client_ids(
        self, timeout: Optional[int] = _DEFAULT_OIDC_CLIENT_IDS_TIMEOUT
    ) -> Dict[str, _OIDCClientID]:
        """Receive OIDC client ID responses from pods.

        These will be the first step in OIDC-related auth flows, showing the modeller
        that the pods have received their request and are ready to start the flow.

        Returns:
            A mapping of pod identifier to their client ID as a dataclass.
        """
        oidc_client_ids: Dict[str, _OIDCClientID] = {}

        def _oidc_client_id_message_handler(message: _BitfountMessage) -> None:
            logger.info(f"Received OIDC Client ID from {message.sender}")
            decrypted_msg = self._decrypt_message(message)
            oidc_client_ids[decrypted_msg.sender] = _OIDCClientID.deserialize(
                decrypted_msg.body
            )

        # Create handler for processing the group of expected responses. Using it
        # as a context manager guarantees that the handlers are correctly applied
        # and removed.
        with _AsyncMultipleResponsesHandler(
            handler=_oidc_client_id_message_handler,
            message_types=_BitfountMessageType.OIDC_CHALLENGE,
            mailbox=self,
            responders=self._pod_identifiers,
        ) as multi_response:
            try:
                # Wait for all responses to have been received or until the
                # timeout expires.
                await multi_response.wait_for_responses(timeout=timeout)
            except MessageRetrievalError as err:
                logger.error(
                    f"Error receiving responses from all pods to the OIDC phase "
                    f"of the task request: {err}"
                )
                raise BitfountTaskStartError("Failed to start task with all pods.")

        if not oidc_client_ids:
            logger.error("No OIDC client id retreived from message handler")
            raise ValueError("No OIDC client id retreived from message handler")

        return oidc_client_ids

    async def send_oidc_auth_flow_responses(
        self,
        oidc_responses: Dict[str, _OIDCAuthFlowResponse],
    ) -> None:
        """Send response for OIDC Authorization Code Flow."""
        for pod_id, response in oidc_responses.items():
            pod_mailbox = self.worker_mailboxes[pod_id]
            await _send_aes_encrypted_message(
                response.serialize(),
                pod_mailbox.aes_encryption_key,
                self.message_service,
                message_type=_BitfountMessageType.OIDC_AFC_PKCE_RESPONSE,
                recipient=pod_mailbox.pod_identifier,
                recipient_mailbox_id=pod_mailbox.mailbox_id,
                sender=self.message_service.username,
                sender_mailbox_id=self.mailbox_id,
            )

    async def send_oidc_device_code_responses(
        self, device_code_details: Dict[str, _PodDeviceCodeDetails]
    ) -> None:
        """Send response for OIDC Device Code Flow."""
        for pod_id, details in device_code_details.items():
            pod_mailbox = self.worker_mailboxes[pod_id]
            await _send_aes_encrypted_message(
                details.serialize(),
                pod_mailbox.aes_encryption_key,
                self.message_service,
                message_type=_BitfountMessageType.OIDC_DEVICE_CODE_RESPONSE,
                recipient=pod_mailbox.pod_identifier,
                recipient_mailbox_id=pod_mailbox.mailbox_id,
                sender=self.message_service.username,
                sender_mailbox_id=self.mailbox_id,
            )

    async def get_saml_challenges(
        self, timeout: int = _DEFAULT_TASK_RESPONSE_TIMEOUT
    ) -> List[_DecryptedBitfountMessage]:
        """Process incoming SAML Challenges.

        Incoming responses are awaited as a group until all are received or timeout
        is reached. Responses are expected from all pods assigned at mailbox init.

        Returns:
            A list of received SAML challenges.
        """
        saml_challenges = []

        def _saml_challenge_message_handler(message: _BitfountMessage) -> None:
            """Simple handler that saves messages to closured dict."""
            logger.info(
                f"Received message with type: {message.message_type} "
                f"from sender: {message.sender}"
            )
            saml_challenges.append(self._decrypt_message(message))

        # Create handler for processing the group of expected responses. Using it
        # as a context manager guarantees that the handlers are correctly applied
        # and removed.
        with _AsyncMultipleResponsesHandler(
            handler=_saml_challenge_message_handler,
            message_types=_BitfountMessageType.SAML_REQUEST,
            mailbox=self,
            responders=self._pod_identifiers,
        ) as multi_response:
            try:
                # Wait for all responses to have been received or until the
                # timeout expires.
                await multi_response.wait_for_responses(timeout=timeout)
            except MessageRetrievalError as err:
                logger.error(
                    f"Error receiving responses from all pods to the task request: "
                    f"{err}"
                )
                raise BitfountTaskStartError("Failed to start task with all pods.")

        return saml_challenges

    async def process_task_request_responses(
        self, timeout: int = _DEFAULT_TASK_RESPONSE_TIMEOUT
    ) -> Dict[str, _WorkerMailboxDetails]:
        """Process incoming responses to a task request.

        Incoming responses are awaited as a group until all are received or timeout
        is reached. Responses are expected from all pods assigned at mailbox init.

        Returns:
            The subdict of this mailbox's worker mailboxes that corresponds to
            pods that accepted the task.
        """
        # Set the responses all to None to begin with and replace them with
        # messages as we receive them.
        response_messages: Dict[str, Optional[_DecryptedBitfountMessage]] = {
            pod_identifier: None for pod_identifier in self._pod_identifiers
        }

        def _response_message_handler(message: _BitfountMessage) -> None:
            """Simple handler that saves messages to closured dict."""
            logger.info(
                f"Received message with type: {message.message_type} "
                f"from sender: {message.sender}"
            )
            response_messages[message.sender] = self._decrypt_message(message)

        # Create handler for processing the group of expected responses. Using it
        # as a context manager guarantees that the handlers are correctly applied
        # and removed.
        with _AsyncMultipleResponsesHandler(
            handler=_response_message_handler,
            message_types=[
                _BitfountMessageType.JOB_ACCEPT,
                _BitfountMessageType.JOB_REJECT,
            ],
            mailbox=self,
            responders=self._pod_identifiers,
        ) as multi_response:
            try:
                # Wait for all responses to have been received or until the
                # timeout expires.
                await multi_response.wait_for_responses(timeout=timeout)
            except MessageRetrievalError as err:
                logger.error(
                    f"Error receiving responses from all pods to the task request: "
                    f"{err}"
                )
                raise BitfountTaskStartError("Failed to start task with all pods.")

        accepted_mailbox_details = await self._handle_task_responses(response_messages)

        # Set on the attribute and return as well
        self.accepted_worker_mailboxes = accepted_mailbox_details
        return accepted_mailbox_details

    async def _handle_task_responses(
        self,
        response_messages: MutableMapping[str, Optional[_DecryptedBitfountMessage]],
    ) -> Dict[str, _WorkerMailboxDetails]:
        # Want to track the various responses separately, but only care about
        # the details of the accepted ones.
        accepted_task_worker_mailboxes: Dict[str, _WorkerMailboxDetails] = {}
        # These are effectively only used for counting,
        # so could be replaced with counters.
        # The only reason for creating a list of messages here
        # was in case we wanted to log these errors in future
        rejected_tasks: List[_DecryptedBitfountMessage] = []
        ignored_tasks: List[None] = []

        # Check through each of the responses
        for pod_identifier, response in response_messages.items():
            if response:
                pod_identifier = response.sender

                # Handle ACCEPT response
                if _PodResponseType.ACCEPT.name in response.body:
                    logger.info(f"Pod '{pod_identifier}' accepted request")

                    mailbox_details = self.worker_mailboxes[pod_identifier]
                    accepted_task_worker_mailboxes[pod_identifier] = mailbox_details

                    logger.debug(
                        f"Pod {pod_identifier} " f"mailbox id is: {mailbox_details}"
                    )

                # Handle REJECT response (regardless of what form that reject takes)
                else:
                    rejected_tasks.append(response)

                    # Process different forms of rejection
                    for response_type in response.body:
                        if (
                            response_type
                            == _PodResponseType.SECURE_AGGREGATION_WORKERS_NOT_AUTHORISED.name  # noqa: B950
                        ):
                            unapproved_pods = ", ".join(response.body[response_type])
                            logger.error(
                                f"Received rejection from {pod_identifier}. "
                                f"{_RESPONSE_MESSAGES[_PodResponseType[response_type]]}: "  # noqa: B950
                                f"{unapproved_pods}"
                            )
                        else:
                            logger.error(
                                f"Received rejection from {pod_identifier}. "
                                f"{_RESPONSE_MESSAGES[_PodResponseType[response_type]]}"  # noqa: B950
                            )

            # Handle cases where response didn't arrive
            else:
                response = cast(None, response)
                ignored_tasks.append(response)

        logger.info(
            f"{len(accepted_task_worker_mailboxes)} task(s) accepted, "
            f"{len(rejected_tasks)} rejection(s), "
            f"{len(ignored_tasks)} pod(s) did not respond in time."
        )

        return accepted_task_worker_mailboxes

    async def send_saml_responses(
        self, saml_response: _SAMLResponse, pod_mailbox: _WorkerMailboxDetails
    ) -> None:
        """Send a SAML response to a pod."""
        await _send_aes_encrypted_message(
            saml_response,
            pod_mailbox.aes_encryption_key,
            self.message_service,
            message_type=_BitfountMessageType.SAML_RESPONSE,
            recipient=pod_mailbox.pod_identifier,
            recipient_mailbox_id=pod_mailbox.mailbox_id,
            sender=self.message_service.username,
            sender_mailbox_id=self.mailbox_id,
        )

    ################################
    # End Task Setup Phase Methods #
    ################################

    ##############################
    # Task Running Phase Methods #
    ##############################
    async def _send_to_all_pods_aes_encrypt(
        self, object_to_send: Any, message_type: _BitfountMessageType
    ) -> None:
        """Send message to all pods involved in a training task, AES encrypted.

        Args:
            object_to_send: Body of the message (not encrypted)
            message_type: The type of message to send
        """
        for mailbox in self.accepted_worker_mailboxes.values():
            await _send_aes_encrypted_message(
                object_to_send,
                mailbox.aes_encryption_key,
                self.message_service,
                message_type=message_type,
                recipient=mailbox.pod_identifier,
                recipient_mailbox_id=mailbox.mailbox_id,
                sender_mailbox_id=self.mailbox_id,
                sender=self.message_service.username,
            )

    async def send_training_iteration_complete_update(
        self, training_complete: bool
    ) -> None:
        """Sends whether training is complete or not to the workers."""
        await self._send_to_all_pods_aes_encrypt(
            training_complete, _BitfountMessageType.TRAINING_COMPLETE
        )

    async def send_task_complete_message(self) -> None:
        """Sends task complete message to the workers.

        Note: The message is not important here, the message type is.
        """
        await self._send_to_all_pods_aes_encrypt(
            None, _BitfountMessageType.TASK_COMPLETE
        )

    def _decrypt_message(self, message: _BitfountMessage) -> _DecryptedBitfountMessage:
        """Decrypt received message using this mailbox's AES keys.

        Args:
            message: Received message to decrypt.

        Returns:
            The decrypted message body.
        """
        return message.decrypt(self.worker_mailboxes[message.sender].aes_encryption_key)

    async def get_evaluation_results_from_workers(
        self, timeout: Optional[int] = None
    ) -> List[Any]:
        """Get evaluation results from workers."""
        all_eval_results: List[Any] = []

        # Create light-weight handler to append to shared list
        def evaluation_results_handler(message: _BitfountMessage) -> None:
            logger.debug(f"Receiving evaluation results from worker {message.sender}")
            eval_results = self._decrypt_message(message).body
            all_eval_results.append(eval_results)

        # We use `self` rather than `self.modeller_mailbox` as the mailbox below
        # because this is ensures things are correctly delegated.
        with _AsyncMultipleResponsesHandler(
            handler=evaluation_results_handler,
            message_types=_BitfountMessageType.EVALUATION_RESULTS,
            mailbox=self,
            responders=self.accepted_worker_mailboxes.keys(),
        ) as response_handler:
            await response_handler.wait_for_responses(timeout=timeout)

        return all_eval_results

    async def log(self, message: Mapping[str, object]) -> None:
        """Log message to all pods involved in task."""
        await self._send_to_all_pods_aes_encrypt(
            message, _BitfountMessageType.LOG_MESSAGE
        )

    def _setup_federated_logging(self) -> None:
        """Set up federated logging."""
        _federate_logger(self)

        def log_message_handler(message: _BitfountMessage) -> None:
            """Locally logs the log message that has been received from a pod."""
            log_message_wrapper: _DecryptedBitfountMessage = self._decrypt_message(
                message
            )
            log_message: _JSONDict = log_message_wrapper.body
            # We prepend the name of the pod to the log message
            log_message["msg"] = f"{message.sender} Pod: {log_message['msg']}"
            # We remove the `federated` key to avoid recursively sending a federated
            # log message on both the Modeller and Worker sides
            log_message.pop("federated")
            logger.handle(logging.makeLogRecord(log_message))

        self.register_handler(_BitfountMessageType.LOG_MESSAGE, log_message_handler)

    def _setup_online_status_handler(self) -> None:
        """Respond to online status requests from Pods."""

        async def status_request_handler(message: _BitfountMessage) -> None:
            """Responds to an ONLINE_CHECK request with an ONLINE_RESPONSE."""
            logger.info(f"Informing {message.sender} that we are still online.")
            await _send_aes_encrypted_message(
                None,
                self.accepted_worker_mailboxes[message.sender].aes_encryption_key,
                self.message_service,
                message_type=_BitfountMessageType.ONLINE_RESPONSE,
                recipient=message.sender,
                recipient_mailbox_id=message.sender_mailbox_id,
                sender=self.message_service.username,
                sender_mailbox_id=self.mailbox_id,
            )

        self.register_handler(_BitfountMessageType.ONLINE_CHECK, status_request_handler)

    ##################################
    # End Task Running Phase Methods #
    ##################################


async def _send_model_parameters(
    model_parameters: _SerializedWeights, modeller_mailbox: _ModellerMailbox
) -> None:
    """Sends model parameters to the workers."""
    # Deliberate access to private method here as that method shouldn't be used in
    # any other context than transport layer access.
    # noinspection PyProtectedMember
    await modeller_mailbox._send_to_all_pods_aes_encrypt(
        model_parameters, _BitfountMessageType.MODEL_PARAMETERS
    )


def _training_metrics_handler(
    modeller_mailbox: _ModellerMailbox,
    training_metrics: MutableSequence[Mapping[str, str]],
) -> Callable[[_BitfountMessage], None]:
    """Training metrics handler.

    Will mutate the passed in sequence by appending responses to it.
    """

    def training_metrics_handler(message: _BitfountMessage) -> None:
        logger.debug(f"Receiving training metrics update from worker {message.sender}")
        # Deliberate access to private method here as that method shouldn't be used in
        # any other context than transport layer access.
        # noinspection PyProtectedMember
        single_training_metrics = modeller_mailbox._decrypt_message(message).body
        training_metrics.append(single_training_metrics)

    return training_metrics_handler


async def _get_training_metrics_from_workers(
    modeller_mailbox: _ModellerMailbox,
    timeout: Optional[int] = None,
) -> Dict[str, float]:
    """Get training metrics from workers."""
    training_metrics: List[Mapping[str, str]] = []
    training_metrics_handler = _training_metrics_handler(
        modeller_mailbox, training_metrics
    )
    with _AsyncMultipleResponsesHandler(
        handler=training_metrics_handler,
        message_types=_BitfountMessageType.TRAINING_METRICS,
        mailbox=modeller_mailbox,
        responders=modeller_mailbox.accepted_worker_mailboxes.keys(),
    ) as response_handler:
        non_responders = await response_handler.wait_for_responses(timeout=timeout)
        if non_responders:
            logger.info(
                f"The following did not send training metrics in time: {non_responders}"
            )

    # Find the average metrics for those who responded and return
    averaged_training_metrics = _average_training_metrics(training_metrics)
    return averaged_training_metrics


def _parameter_updates_handler(
    modeller_mailbox: _ModellerMailbox,
    weight_updates: MutableMapping[str, _SerializedWeights],
) -> Callable[[_BitfountMessage], None]:
    """Parameter update handler.

    Will mutate the passed in sequence by appending responses to it.
    """

    def parameter_update_handler(message: _BitfountMessage) -> None:
        logger.debug(f"Receiving parameter update from worker {message.sender}")
        # Deliberate access to private method here as that method shouldn't be used in
        # any other context than transport layer access.
        # noinspection PyProtectedMember
        weight_update = modeller_mailbox._decrypt_message(message).body
        sender = message.sender
        weight_updates[sender] = weight_update

    return parameter_update_handler


async def _get_parameter_updates_from_workers(
    modeller_mailbox: _ModellerMailbox, timeout: Optional[int] = None
) -> Dict[str, _SerializedWeights]:
    """Get model parameter updates from workers."""
    weight_updates: Dict[str, _SerializedWeights] = {}
    parameter_updates_handler = _parameter_updates_handler(
        modeller_mailbox, weight_updates
    )

    with _AsyncMultipleResponsesHandler(
        handler=parameter_updates_handler,
        message_types=_BitfountMessageType.TRAINING_UPDATE,
        mailbox=modeller_mailbox,
        responders=modeller_mailbox.accepted_worker_mailboxes.keys(),
    ) as response_handler:
        await response_handler.wait_for_responses(timeout=timeout)

    return weight_updates
