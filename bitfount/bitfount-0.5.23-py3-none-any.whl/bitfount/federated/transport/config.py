"""Message Service configuration."""
from dataclasses import dataclass
import logging

# gRPC stubs don't cover grpc.aio yet
from grpc import aio  # type: ignore[attr-defined] # Reason: see comment
from grpc import ssl_channel_credentials

from bitfount.federated.transport import _MESSAGE_SERVICE_GRPC_OPTIONS
from bitfount.federated.transport.protos.messages_pb2_grpc import MessageServiceStub

logger = logging.getLogger(__name__)

#: Production message service URL.
PRODUCTION_MESSAGE_SERVICE_URL = "messaging.bitfount.com"
_STAGING_MESSAGE_SERVICE_URL = "messaging.staging.bitfount.com"
_DEV_MESSAGE_SERVICE_URL = "localhost"
_DEV_MESSAGE_SERVICE_PORT = 5001
_DEV_MESSAGE_SERVICE_TLS = False


@dataclass
class MessageServiceConfig:
    """Configuration for the message service.

    Args:
        url: The URL of the message service. Defaults to
            `PRODUCTION_MESSAGE_SERVICE_URL`.
        port: The port of the message service. Defaults to 443.
        tls: Whether to use TLS. Defaults to True.
        use_local_storage: Whether to use local storage instead of communicating via the
            message service if both parties are on the same device. This can be used to
            remove the overhead of communication. Defaults to False.

    Raises:
        ValueError: If `tls` is False and `url` is a Bitfount URL.
    """

    url: str = PRODUCTION_MESSAGE_SERVICE_URL
    port: int = 443
    tls: bool = True  # only used for development
    use_local_storage: bool = False

    def __post_init__(self) -> None:
        if not self.tls and ".bitfount.com" in self.url:
            raise ValueError(
                "TLS disabled. Message service communication must be with TLS."
            )
        elif not self.tls:
            logger.warning("Message service communication without TLS.")

    # @cached_property can't be used because it returns the _exact_ same Awaitable
    # which cannot be awaited more than once.
    @property
    async def stub(self) -> MessageServiceStub:
        """Creates and returns message service stub from this config."""
        # This method must be kept as async def to ensure that the channel
        # creation occurs on the correct event loop.
        if self.tls:
            # This is an async secure_channel
            channel = aio.secure_channel(
                f"{self.url}:{self.port}",
                ssl_channel_credentials(),
                options=_MESSAGE_SERVICE_GRPC_OPTIONS,
            )
        else:
            # This is an async insecure_channel
            channel = aio.insecure_channel(
                f"{self.url}:{self.port}", options=_MESSAGE_SERVICE_GRPC_OPTIONS
            )

        return MessageServiceStub(channel)
