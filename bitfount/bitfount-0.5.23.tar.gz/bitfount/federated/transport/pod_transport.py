"""Handling incoming tasks for a Pod."""
from __future__ import annotations

from typing import Mapping, Optional

from grpc import RpcError

from bitfount.federated.exceptions import PodConnectFailedError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.transport.base_transport import Handler, _BaseMailbox
from bitfount.federated.transport.message_service import (
    _BitfountMessageType,
    _MessageService,
)

DEFAULT_KEY_EXCHANGE_TIMEOUT: int = 2 * 60

logger = _get_federated_logger(__name__)


class _PodMailbox(_BaseMailbox):
    """Handling of incoming training tasks from modellers."""

    def __init__(
        self,
        pod_name: str,
        mailbox_id: str,
        message_service: _MessageService,
        handlers: Optional[Mapping[_BitfountMessageType, Handler]] = None,
    ):
        """Creates a new pod mailbox.

        Note that the preferred way to get a new PodMailbox is by calling
        PodMailbox.connect_pod() which will instantiate the correct PodMailbox
        for you.

        Args:
            pod_name: The name of the pod.
            mailbox_id: The mailbox ID for this pod on the message service.
            message_service: The message service to use.
            handlers: Optional. A set of handlers to initialise with.
        """
        super().__init__(
            mailbox_id=mailbox_id, message_service=message_service, handlers=handlers
        )
        self.pod_name = pod_name
        self.pod_identifier = f"{self.message_service.username}/{self.pod_name}"

    @classmethod
    async def connect_pod(
        cls, pod_name: str, message_service: _MessageService
    ) -> _PodMailbox:
        """Registers with message service and created mailbox.

        Returns:
            The created mailbox.

        Raises:
            RuntimeError: If a GRPC error occurs or the message service is
                          unable to connect the pod.
        """
        logger.info(f"Connecting to messaging service as: {pod_name}")
        try:
            mailbox_id = await message_service.connect_pod(pod_name)
        except (RpcError, PodConnectFailedError) as err:
            logger.critical(
                "Error occurred when trying to call PodConnect on messaging service"
            )
            raise PodConnectFailedError(
                f"Failed to connect to messaging service "
                f"as pod: {pod_name}. Error: {err}"
            )

        pod_mailbox = cls(
            pod_name=pod_name, mailbox_id=mailbox_id, message_service=message_service
        )

        return pod_mailbox
