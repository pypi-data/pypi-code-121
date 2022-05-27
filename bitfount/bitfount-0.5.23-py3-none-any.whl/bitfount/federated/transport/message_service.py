"""Interface classes and methods for the message service.

Provides functionality to wrap generated GRPC code and python-friendly versions
of GRPC classes and methods.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from math import ceil
import os
import platform
import sys
import tempfile
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    Final,
    Mapping,
    Optional,
    Tuple,
    Union,
    cast,
)
from urllib.parse import urlparse

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from grpc import RpcError, StatusCode
import msgpack
import numpy as np
import pandas as pd
import psutil
import pyarrow as pa
from pyarrow import feather
from requests.exceptions import RequestException

from bitfount.config import get_gpu_metadata
from bitfount.federated.encryption import _AESEncryption, _RSAEncryption
from bitfount.federated.exceptions import PodConnectFailedError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.federated.transport.exceptions import BitfountMessageServiceError
from bitfount.federated.transport.protos.messages_pb2 import (
    BitfountMessage as GrpcBitfountMessage,
)
from bitfount.federated.transport.protos.messages_pb2 import (
    BitfountTask,
    BitfountTasks,
    CommunicationDetails,
    LargeStorageRequest,
    PodData,
    SuccessResponse,
)
from bitfount.federated.transport.protos.messages_pb2 import Acknowledgement
from bitfount.federated.transport.protos.messages_pb2_grpc import MessageServiceStub
from bitfount.storage import (
    _async_download_data_from_s3,
    _async_upload_data_to_s3,
    _get_packed_data_object_size,
)
from bitfount.types import _S3PresignedPOSTFields, _S3PresignedPOSTURL, _S3PresignedURL
from bitfount.utils import _get_mb_from_bytes

if TYPE_CHECKING:
    from bitfount.hub.authentication_flow import BitfountSession

logger = _get_federated_logger(__name__)

# This is used for sanity checking/detecting when the message body is an S3 URL.
# However, it doesn't give us any security guarantees as this suffix may not be
# unique to us.
_S3_NETLOC_SUFFIX: str = "-message-service-external.s3.eu-west-2.amazonaws.com"

# This limit is lower than the SQS message limit intentionally.
# When messages are packaged on the message service we attach some metadata,
# the metadata will make them larger, so the python code needs a lower limit.
# So this limit ensures that our message service will accept the raw messages.
_SMALL_MESSAGE_UPPER_LIMIT_SIZE_BYTES: int = 100 * 1024  # 100kb

# Maximum storage request size in message service: 3gb. This should match the value
# in bitfount/message-service:src/messaging/queue.service.ts
_MAX_STORAGE_SIZE_BYTES: Final[int] = 3 * 1024 * 1024 * 1024
_MAX_STORAGE_SIZE_MEGABYTES: Final[int] = _get_mb_from_bytes(
    _MAX_STORAGE_SIZE_BYTES
).whole

# Create fibonacci backoffs to avoid constant querying for messages. Will poll
# (60/1=60) times the first minute after the last message (i.e. 1s intervals),
# (60/2=30) times (i.e. 2s intervals) for the second minute, etc, up to a max of
# 8s polling intervals.
_POLLING_BACKOFFS: Final[Tuple[int, ...]] = tuple(
    i for i in (1, 2, 3, 5, 8) for _ in range(ceil(60 / i))
)


def _current_time() -> str:
    """Gets current time as factory for dataclass timestamps."""
    return datetime.now().isoformat()


def msgpackext_encode(obj: Any) -> Any:
    """Serialises extension objects for DataFrames or np.ndarray using pyarrow.

    Args:
        obj: An object to be serialized
    Returns:
        A msgpack compatible extension form of the object.
    """
    if isinstance(obj, np.ndarray):
        tensor = pa.Tensor.from_numpy(obj)
        sink = pa.BufferOutputStream()
        pa.ipc.write_tensor(tensor, sink)
        buf = sink.getvalue().to_pybytes()
        return msgpack.ExtType(1, buf)

    if isinstance(obj, pd.DataFrame):
        sink = pa.BufferOutputStream()
        feather.write_feather(obj, sink)
        buf = sink.getvalue().to_pybytes()
        return msgpack.ExtType(2, buf)
    return obj


def msgpackext_decode(code: int, obj: Any) -> Any:
    """Extension to deserialise DataFrame and numpy using arrow.

    Args:
        code: An integer specifying whether the object is
            a numpy array (code=1) or Dataframe (code=2).
        obj: An encoded object, likely a dictionary.

    Returns:
        The decoded form of the object.
    """
    if code == 1:
        buf = pa.py_buffer(obj)
        tensor = pa.ipc.read_tensor(buf)
        return tensor.to_numpy()
    elif code == 2:
        return feather.read_feather(pa.py_buffer(obj))
    return obj


class _BitfountMessageType(Enum):
    """Used for providing information on the expected shape of a Message.

    These can be used to quickly identify the expected type of an unstructured message
    body from the message service.

    These message types are defined in 3 other locations and any changes need to be
    reflected in all locations:

     - in the proto file
     - in the message service
     - in the Hub/AM for audit logs
    """

    SAML_REQUEST = GrpcBitfountMessage.SAML_REQUEST
    SAML_RESPONSE = GrpcBitfountMessage.SAML_RESPONSE
    ALGORITHM_EXCHANGE = GrpcBitfountMessage.ALGORITHM_EXCHANGE
    # TODO: [BIT-1049] Should these be combined into JOB_RESPONSE?
    #       The message body itself indicates whether it was an accept or reject.
    JOB_ACCEPT = GrpcBitfountMessage.JOB_ACCEPT
    JOB_REJECT = GrpcBitfountMessage.JOB_REJECT
    JOB_REQUEST = GrpcBitfountMessage.JOB_REQUEST
    EVALUATION_RESULTS = GrpcBitfountMessage.EVALUATION_RESULTS
    KEY_EXCHANGE = GrpcBitfountMessage.KEY_EXCHANGE
    LOG_MESSAGE = GrpcBitfountMessage.LOG_MESSAGE
    # weight updates sent modeller->worker
    MODEL_PARAMETERS = GrpcBitfountMessage.MODEL_PARAMETERS
    SECURE_SHARE = GrpcBitfountMessage.SECURE_SHARE
    TRAINING_COMPLETE = GrpcBitfountMessage.TRAINING_COMPLETE
    # task complete message modeller->worker
    TASK_COMPLETE = GrpcBitfountMessage.TASK_COMPLETE
    # task abort message worker->modeller
    TASK_ABORT = GrpcBitfountMessage.TASK_ABORT
    # weight updates send worker->modeller
    TRAINING_UPDATE = GrpcBitfountMessage.TRAINING_UPDATE
    # validation metrics sent worker->modeller
    TRAINING_METRICS = GrpcBitfountMessage.TRAINING_METRICS
    # Default value for Proto
    UNDEFINED = GrpcBitfountMessage.UNDEFINED
    # OIDC identity verification related types
    OIDC_CHALLENGE = GrpcBitfountMessage.OIDC_CHALLENGE
    # Authorisation Flow Code with PKCE Response
    OIDC_AFC_PKCE_RESPONSE = GrpcBitfountMessage.OIDC_AFC_PKCE_RESPONSE
    # Device Code Response
    OIDC_DEVICE_CODE_RESPONSE = GrpcBitfountMessage.OIDC_DEVICE_CODE_RESPONSE
    # Online check from worker->modeller
    ONLINE_CHECK = GrpcBitfountMessage.ONLINE_CHECK
    # Online response from modeller->worker
    ONLINE_RESPONSE = GrpcBitfountMessage.ONLINE_RESPONSE


class _LargeObjectRequestHandler:
    """Slim wrapper for handling requests to blob storage."""

    @staticmethod
    async def upload_large_object(
        upload_url: _S3PresignedPOSTURL,
        upload_fields: _S3PresignedPOSTFields,
        large_object: bytes,
    ) -> None:
        """Uploads the object to the upload URL.

        Args:
            upload_url: The URL to upload to.
            upload_fields: Additional data fields needed to upload the object.
            large_object: The object to upload as bytes.

        Raises:
            HTTPError: If the upload fails.
        """
        try:
            await _async_upload_data_to_s3(upload_url, upload_fields, large_object)
        except RequestException as ex:
            raise RequestException(
                f"Failed to upload message to large message storage. Cause: {str(ex)}."
            ) from ex

    @staticmethod
    async def get_large_object_from_url(url: _S3PresignedURL) -> bytes:
        """Retrieves a larger message from the provided download URL.

        Args:
            url: The URL provided on the message service.

        Returns:
            The message that was uploaded.

        Raises:
            HTTPError: If the download fails
        """
        try:
            # We can guarantee the return type is bytes as `upload_large_object`
            # takes in bytes.
            large_object: bytes = await _async_download_data_from_s3(url)
            return large_object
        except RequestException as ex:
            raise RequestException(
                f"Failed to retrieve message from large message storage."
                f" Cause: {str(ex)}."
            ) from ex


@dataclass
class _BitfountMessage:
    """A common message structure for all messages from the message service.

    This is a pythonic wrapper on the generated gRPC Proto,
    allowing us to pre-emptively build in support for upcoming features
    as well as backwards compatibility where needed.
    """

    message_type: _BitfountMessageType
    body: bytes
    recipient: str
    recipient_mailbox_id: str
    sender: str
    sender_mailbox_id: str
    # This is provided to pods for secure aggregation
    pod_mailbox_ids: Dict[str, str] = field(default_factory=dict)
    # default_factory is used here to ensure current time is set for each instantiation
    timestamp: str = field(default_factory=_current_time)
    # Provided by the message service
    receipt_handle: Optional[str] = None

    @staticmethod
    async def from_rpc(message: GrpcBitfountMessage) -> _BitfountMessage:
        """Converts Proto messages into a BitfountMessage.

        Currently requires some additional logic due to the differing protos,
        FromModeller & FromPod, but hopefully those will soon be one proto.

        Args:
            message: A message from a pod or modeller.

        Returns: A BitfountMessage containing the data from the original message

        """
        message_body: bytes = message.body
        try:
            # We attempt to unpack this, as we need to know if it is:
            #   bytes  - Encrypted
            #   string - A URL to download the message body from
            unpacked_body_to_inspect: Union[str, bytes] = msgpack.loads(
                message.body, ext_hook=msgpackext_decode
            )

            # Checks if message body is an S3 file reference or local file reference
            if isinstance(unpacked_body_to_inspect, str):
                parsed_url = urlparse(unpacked_body_to_inspect)
                # If it is an S3 file reference, retrieve the actual message from S3
                if parsed_url.scheme == "https" and parsed_url.netloc.endswith(
                    _S3_NETLOC_SUFFIX
                ):
                    logger.debug("Large message, retrieving from large object storage")
                    storage_url = cast(_S3PresignedURL, unpacked_body_to_inspect)
                    message_body = (
                        await _LargeObjectRequestHandler.get_large_object_from_url(
                            storage_url
                        )
                    )
                # If it is a local file reference,
                # retrieve the actual message and re-parse
                # the message with the file contents
                # For windows, the letter corresponding to
                # the local drive gets assigned to the scheme,
                # so we need an additional check.
                elif (
                    (
                        not parsed_url.scheme
                        or (
                            len(parsed_url.scheme) == 1
                            and sys.platform in ["win32", "win64"]
                        )
                    )
                    and not parsed_url.netloc
                    and parsed_url.path
                ):
                    logger.debug("Local message, retrieving from local storage")
                    with open(unpacked_body_to_inspect, "rb") as f:
                        message_body = f.read()
                    os.remove(
                        unpacked_body_to_inspect
                    )  # deletes the tempfile after contents have been read
        except (msgpack.exceptions.UnpackException, ValueError):
            logger.debug(
                "Couldn't unpack message - "
                "The message is most likely an encrypted message "
                "which is not on blob storage"
            )

        return _BitfountMessage(
            message_type=_BitfountMessageType(message.messageType),
            body=message_body,
            recipient=message.recipient,
            recipient_mailbox_id=message.recipientMailboxId,
            sender=message.sender,
            sender_mailbox_id=message.senderMailboxId,
            pod_mailbox_ids=message.podMailboxIds,
            receipt_handle=message.receiptHandle,
            timestamp=message.timestamp,
        )

    def decrypt(self, aes_key: bytes) -> _DecryptedBitfountMessage:
        """Decrypt message body using AES.

        Args:
            aes_key: AES Key to use for decryption
        """
        decrypted_message_body = msgpack.loads(
            _MessageEncryption.decrypt_incoming_message(self.body, aes_key),
            ext_hook=msgpackext_decode,
        )
        return _DecryptedBitfountMessage(
            message_type=self.message_type,
            body=decrypted_message_body,
            recipient=self.recipient,
            recipient_mailbox_id=self.recipient_mailbox_id,
            sender=self.sender,
            sender_mailbox_id=self.sender_mailbox_id,
            pod_mailbox_ids=self.pod_mailbox_ids,
            timestamp=self.timestamp,
        )

    def decrypt_rsa(self, private_key: RSAPrivateKey) -> _DecryptedBitfountMessage:
        """Decrypt message body using RSA.

        Args:
            private_key: RSA private key to use for decryption.
        """
        decrypted_message_body: Any = msgpack.loads(
            _RSAEncryption.decrypt(self.body, private_key)
        )
        return _DecryptedBitfountMessage(
            message_type=self.message_type,
            body=decrypted_message_body,
            recipient=self.recipient,
            recipient_mailbox_id=self.recipient_mailbox_id,
            sender=self.sender,
            sender_mailbox_id=self.sender_mailbox_id,
            pod_mailbox_ids=self.pod_mailbox_ids,
            timestamp=self.timestamp,
        )


@dataclass
class _DecryptedBitfountMessage:
    """BitfountMessage where the body has been decrypted.

    This gives us more confidence that we have a decrypted body,
    and allows us to pass around the decrypted message body and
    metadata together easily.
    """

    message_type: _BitfountMessageType
    body: Any
    recipient: str
    recipient_mailbox_id: str
    sender: str
    sender_mailbox_id: str
    # This is provided to pods for secure aggregation
    pod_mailbox_ids: Dict[str, str] = field(default_factory=dict)
    # default_factory is used here to ensure current time is set for each instantiation
    timestamp: str = field(default_factory=_current_time)


class _MessageService:
    """Slim wrapper around the GRPC Functions provided by the message service.

    It stops the GRPC objects which aren't very pleasant to use from being everywhere
    as well as making it easier to replace these in future if needed.

    Args:
        session: Used for authentication.
        config: The configuration for the gRPC message service.
    """

    def __init__(self, session: BitfountSession, config: MessageServiceConfig):
        self.session = session
        self.config = config
        self.use_local_storage: bool = config.use_local_storage
        self._stub: Optional[MessageServiceStub] = None

    # @cached_property can't be used because it returns the _exact_ same Awaitable
    # which cannot be awaited more than once.
    @property
    async def stub(self) -> MessageServiceStub:
        """The gRPC stub generated for this instance."""
        if self._stub is None:
            self._stub = await self.config.stub
        return self._stub

    @property
    def username(self) -> str:
        """Get the authenticated username."""
        return self.session.username

    async def connect_pod(self, pod_name: str) -> str:
        """Make the message service aware of the Pod.

        This ensures that the correct queue is set up for this pod,
        in future it may contain more metadata.

        Args:
            pod_name: The name of the pod (the part after 'username/')

        Returns:
            The created mailbox ID for this pod.

        Raises:
            BitfountMessageServiceError: If an error occurs when communicating
                                         with the message service.
        """
        processor = platform.processor()
        pod_os = platform.system()
        logical_cpu_count = psutil.cpu_count()
        total_physical_memory_bytes = psutil.virtual_memory().total
        gpu_name, available_gpus = get_gpu_metadata()

        try:
            logger.debug("Accessing gRPC stub.")
            stub = await self.stub
            logger.debug("Calling PodConnect on message service.")
            response = await stub.PodConnect(
                PodData(
                    podName=pod_name,
                    processor=processor,
                    podOS=pod_os,
                    cpuCount=logical_cpu_count,
                    totalMemoryBytes=total_physical_memory_bytes,
                    gpuCount=available_gpus,
                    gpuName=gpu_name,
                ),
                metadata=[("token", self.session.access_token)],
            )
            logger.debug(f"PodConnect completed, response: {response}")
        except (RpcError, RequestException) as e:
            logger.debug(e, exc_info=True)
            raise BitfountMessageServiceError(
                "Unable to connect pod to message service."
                " See debug logs for more details."
            )

        # If we've not received a successful response (but no other RPC error
        # happened) then raise it here.
        if not isinstance(response, SuccessResponse):
            raise PodConnectFailedError("Unable to connect pod to message service.")

        # TODO: [BIT-960] Currently this is just hardcoded to return the pod_name
        #       (which is what the mailbox ID will actually be). [BIT-960] will have
        #       the PodConnect method actually return the generated mailbox ID so
        #       that if the approach changes in future it only needs to change on
        #       the message service side. At that point this should return the
        #       generated mailbox ID instead.
        return pod_name

    async def setup_communication_with_pods(
        self, tasks_per_pod: Mapping[str, bytes]
    ) -> Tuple[str, Dict[str, str]]:
        """Called by the modeller to set up communication channels with specified pods.

        Args:
            tasks_per_pod: Mapping of pod identifiers to AES Encrypted messages.

        Returns:
            A tuple of mailbox IDs used for communications:
                - mailbox_id (str): The modeller's mailbox ID
                - worker_mailbox_ids (dict): Mapping from Pod ID to Worker Mailbox ID

        Raises:
            BitfountMessageServiceError: If an error occurs when communicating
                                         with the message service.
        """
        logger.debug(f"Sending task request to: '{tasks_per_pod.keys()}'")
        try:
            communication_details = await (await self.stub).SetupTaskMailboxes(
                BitfountTasks(
                    tasks=[
                        BitfountTask(
                            podIdentifier=pod_identifier,
                            encryptedTask=aes_encrypted_task,
                        )
                        for pod_identifier, aes_encrypted_task in tasks_per_pod.items()
                    ]
                ),
                metadata=[("token", self.session.access_token)],
            )
        except (RpcError, RequestException) as e:
            logger.debug(e, exc_info=True)
            raise BitfountMessageServiceError(
                "Unable to setup communication with target pods."
                " See debug logs for more details."
            )

        # communication_details.podMailboxIds is actually the _worker_ mailbox_ids
        return communication_details.mailboxId, communication_details.podMailboxIds

    async def poll_for_messages(
        self,
        mailbox_id: str,
    ) -> AsyncGenerator[_BitfountMessage, None]:
        """Polls target mailbox for message.

        Will keep retrying up to `self.minutes_before_timeout_no_messages`
        or until a message is received, whichever is sooner.

        It has the same behaviour as `get_message` regarding exceptions:
        if exceptions are repeatedly raised then it will throw the exception.

        Args:
            mailbox_id: The mailbox to poll for messages

        Yields:
            BitfountMessage: the next message received
        """
        counter = 0

        while True:
            message = await self._get_message(mailbox_id)

            if message:
                # Reset counter
                counter = 0
                # Yield as soon as we've retrieved a message
                yield message
            else:
                counter += 1
                # Cap counter at the maximum `backoffs` entry
                counter = min(counter, len(_POLLING_BACKOFFS) - 1)

            # Sleep for backoff time until trying again
            await asyncio.sleep(_POLLING_BACKOFFS[counter])

    async def _get_message(
        self,
        mailbox_id: str,
        max_attempts: int = 3,
        wait_between_errors: int = 30,
    ) -> Optional[_BitfountMessage]:
        """Retrieve message from mailbox if available.

        If none are available then it returns None.

        Other errors are raised if they occur repeatedly.

        Args:
            mailbox_id: Mailbox to check for messages.
            max_attempts: Number of times that we will retry if an error occurs.
            wait_between_errors: Time to wait between errors in seconds.

        Returns:
            An BitfountMessage if one is available, else None.

        Raises:
            BitfountMessageServiceError: If an error occurs when multiple times
                                         when communicating with the message service.
        """
        errors_encountered = 0
        delete_mailbox = False

        while errors_encountered < max_attempts:
            try:
                message = await (await self.stub).GetBitfountMessage(
                    CommunicationDetails(mailboxId=mailbox_id),
                    metadata=[("token", self.session.access_token)],
                )

                if message.messageType == _BitfountMessageType.TASK_COMPLETE.value:
                    logging.debug(
                        "Received a TASK_COMPLETE message - "
                        "asking message service to tidy up."
                    )
                    delete_mailbox = True

                await (await self.stub).AcknowledgeMessage(
                    Acknowledgement(
                        mailboxId=mailbox_id,
                        receiptHandle=message.receiptHandle,
                        deleteMailbox=delete_mailbox,
                    ),
                    metadata=[("token", self.session.access_token)],
                )

                return await _BitfountMessage.from_rpc(message)
            except (RpcError, RequestException) as ex:
                # This indicates that no message was waiting
                if isinstance(ex, RpcError) and ex.code() == StatusCode.NOT_FOUND:
                    return None

                errors_encountered += 1
                logger.warning(
                    f"Error retrieving message from mailbox: {mailbox_id}. "
                    f"Error was: {ex}"
                )

                if errors_encountered == max_attempts:
                    logging.debug(ex, exc_info=True)
                    logging.error(
                        f"Exceeded {max_attempts} when retrieving message "
                        f"from {mailbox_id}"
                    )
                    raise BitfountMessageServiceError(
                        "Issue retrieving message from mailbox."
                        " See debug log for details."
                    )

                # The message service already has a 'wait' built in
                # to allow time for messages to arrive
                # but in these other error cases we should wait before retrying
                await asyncio.sleep(wait_between_errors)

        # This shouldn't be reached but is included to make mypy happy
        return None

    async def send_message(
        self,
        message: _BitfountMessage,
        already_packed: bool = False,
    ) -> SuccessResponse:
        """Send a message.

        Args:
            message (BitfountMessage): The message to send
            already_packed (bool): Whether or not the message is already in required
                bytes format

        Returns:
            SuccessResponse if the message was successfully sent

        Raises:
            BitfountMessageServiceError: If an error occurs when communicating
                                         with the message service.
        """
        if not already_packed:
            message.body = msgpack.dumps(
                message.body,
                default=msgpackext_encode,
            )

        if self.use_local_storage:
            message.body = self._save_object_to_local_storage(message)
        else:
            message.body = await self._maybe_upload_to_large_object_storage(message)

        try:
            return await (await self.stub).SendBitfountMessage(
                GrpcBitfountMessage(
                    messageType=message.message_type.value,
                    body=message.body,
                    recipient=message.recipient,
                    recipientMailboxId=message.recipient_mailbox_id,
                    sender=message.sender,
                    senderMailboxId=message.sender_mailbox_id,
                    timestamp=message.timestamp,
                    podMailboxIds=message.pod_mailbox_ids,
                ),
                metadata=[("token", self.session.access_token)],
            )
        except (RpcError, RequestException) as e:
            logger.debug(e, exc_info=True)
            raise BitfountMessageServiceError(
                "Encountered problem when sending message."
                " See debug logs for more details."
            )

    async def _maybe_upload_to_large_object_storage(
        self, message: _BitfountMessage
    ) -> bytes:
        """Uploads the message body to large object storage if it's too big.

        Args:
            message: the message containing the body to upload

        Returns:
            Either the original message body, or a URL that can be used to download it
        """
        # Larger messages are sent as references to large object storage
        if len(message.body) > _SMALL_MESSAGE_UPPER_LIMIT_SIZE_BYTES:
            # Check that message body isn't above the maximum storage size
            message_body_size = _get_packed_data_object_size(message.body)
            if message_body_size > _MAX_STORAGE_SIZE_BYTES:
                raise ValueError(
                    f"Message body is too large to upload: "
                    f"expected max {_MAX_STORAGE_SIZE_MEGABYTES} megabytes, "
                    f"got {_get_mb_from_bytes(message_body_size).fractional} megabytes."
                )

            pod_name = None
            if message.sender and "/" in message.sender:
                pod_name = message.sender.split("/")[1]
            (
                upload_url,
                upload_fields,
            ), download_url = await self._get_large_object_storage_details(
                message.sender_mailbox_id, message_body_size, pod_name
            )
            await _LargeObjectRequestHandler.upload_large_object(
                upload_url, upload_fields, message.body
            )

            # Currently necessary, as the message service is expecting bytes
            return msgpack.dumps(download_url, default=msgpackext_encode)
        # Small messages can just go on the message service directly
        return message.body

    async def _get_large_object_storage_details(
        self, mailbox_id: str, message_size: int, pod_name: Optional[str] = None
    ) -> Tuple[Tuple[_S3PresignedPOSTURL, _S3PresignedPOSTFields], _S3PresignedURL]:
        """Get an upload and download URL for larger message bodies.

        Args:
            mailbox_id: Your mailbox id for the current task.
            message_size: The size of the message to upload (an upper limit).
            pod_name: Name of the pod that you're acting as, if relevant.

        Returns:
            Tuple of upload handler, download URL.

        Raises:
            BitfountMessageServiceError: If an error occurs when communicating
                with the message service.
        """
        try:
            blob_storage_data = await (await self.stub).GetLargeObjectStorage(
                LargeStorageRequest(
                    senderMailboxId=mailbox_id,
                    podName=pod_name,
                    contentSize=message_size,
                ),
                metadata=[("token", self.session.access_token)],
            )
            return (
                (
                    cast(_S3PresignedPOSTURL, blob_storage_data.uploadUrl),
                    cast(_S3PresignedPOSTFields, dict(blob_storage_data.uploadFields)),
                ),
                cast(_S3PresignedURL, blob_storage_data.downloadUrl),
            )
        except (RpcError, RequestException) as e:
            logger.debug(e, exc_info=True)
            raise BitfountMessageServiceError(
                "Unable to acquire large object storage."
                " See debug logs for more details."
            )

    @staticmethod
    def _save_object_to_local_storage(message: _BitfountMessage) -> bytes:
        """Saves object to local storage and returns filename.

        Args:
            message: the message containing the body to upload

        Returns:
            (bytes): A path to the file where the local object has been stored.
        """
        # we use mkstemp here to ensure we have complete control over when the file gets
        # deleted on every OS - unlike e.g. NamedTemporaryFile
        handle, local_tempfile = tempfile.mkstemp()
        # write to the open file handler rather than finding the file by name
        with os.fdopen(handle, "wb") as f:
            f.write(message.body)
        return msgpack.dumps(local_tempfile, default=msgpackext_encode)


class _MessageEncryption:
    """Shared functions for handling encryption/decryption of messages.

    These handle encrypting or decrypting a single or multiple messages
    at the same time using different keys (for different pods)
    """

    @staticmethod
    def encrypt_outgoing_message(body: bytes, encryption_key: bytes) -> bytes:
        """Encrypt `body` using `encryption_key`."""
        body, nonce = _AESEncryption.encrypt(encryption_key, body)
        body += nonce
        return body

    @staticmethod
    def decrypt_incoming_message(
        body: bytes,
        encryption_key: bytes,
    ) -> bytes:
        """Decrypt incoming message."""
        body, nonce = body[:-12], body[-12:]
        body = _AESEncryption.decrypt(encryption_key, nonce, body)

        return body
