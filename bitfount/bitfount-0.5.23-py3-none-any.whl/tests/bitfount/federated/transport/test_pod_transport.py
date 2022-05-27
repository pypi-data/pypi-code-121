"""Test pod can handle incoming training requests."""
from unittest.mock import Mock, create_autospec

from grpc import RpcError
from pytest import fixture, raises

from bitfount.federated.exceptions import PodConnectFailedError
from bitfount.federated.transport.message_service import _MessageService
from bitfount.federated.transport.pod_transport import _PodMailbox
from bitfount.federated.transport.protos.messages_pb2 import SuccessResponse
from tests.utils.helper import unit_test


@unit_test
class TestPodMailbox:
    """Tests for PodMailbox."""

    @fixture
    def pod_namespace(self) -> str:
        """A pod namespace."""
        return "podOwnerUsername"

    @fixture
    def pod_name(self) -> str:
        """A pod name."""
        return "some_pod_name"

    @fixture
    def pod_identifier(self, pod_name: str, pod_namespace: str) -> str:
        """A pod identifier."""
        return f"{pod_namespace}/{pod_name}"

    @fixture
    def pod_mailbox_id(self) -> str:
        """Pod mailbox ID."""
        return "some_mailbox_id"

    @fixture
    def aes_key(self) -> bytes:
        """AES encryption key for encrypting pod message."""
        return b"aeskey_length_16"

    @fixture
    def mock_message_service(self) -> Mock:
        """Mocked message service for GRPC calls."""
        mock_message_service: Mock = create_autospec(_MessageService, instance=True)
        return mock_message_service

    @fixture
    def pod_mailbox(
        self, mock_message_service: Mock, pod_mailbox_id: str, pod_name: str
    ) -> _PodMailbox:
        """The PodMailbox under test."""
        return _PodMailbox(pod_name, pod_mailbox_id, mock_message_service)

    async def test_connect_pod_successful(
        self, mock_message_service: Mock, pod_mailbox: _PodMailbox, pod_name: str
    ) -> None:
        """connect_pod successful."""
        mock_message_service.connect_pod.return_value = SuccessResponse()
        await pod_mailbox.connect_pod(pod_name, mock_message_service)
        mock_message_service.connect_pod.assert_called_once_with(pod_name)

    async def test_connect_pod_unsuccessful(
        self, mock_message_service: Mock, pod_mailbox: _PodMailbox, pod_name: str
    ) -> None:
        """connect_pod fails."""
        mock_message_service.connect_pod.side_effect = RpcError()

        with raises(
            PodConnectFailedError,
            match=f"Failed to connect to messaging service as pod: {pod_name}",
        ):
            await pod_mailbox.connect_pod(pod_name, mock_message_service)

        mock_message_service.connect_pod.assert_called_once_with(pod_name)
