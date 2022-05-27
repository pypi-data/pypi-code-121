"""Fixtures for components that are from the transport layer."""
from typing import Callable, Iterable, Type, Union
from unittest.mock import Mock, create_autospec

from grpc import RpcError, StatusCode
from pytest import fixture
from pytest_mock import MockerFixture
from typing_extensions import TypeAlias

from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _MessageService,
)
from tests.utils.mocks import AsyncIteratorMock

MessageOrException: TypeAlias = Union[
    _BitfountMessage, BaseException, Type[BaseException]
]


@fixture
def mock_grpc_insecure_channel(mocker: MockerFixture) -> Mock:
    """Mock out grpc.insecure_channel() import in the config module.

    As aio is imported by `from grpc import aio` in the config module we need to
    mock it out that way.
    """
    mock_insecure_channel: Mock = mocker.patch(
        "grpc.aio.insecure_channel", autospec=True
    )
    return mock_insecure_channel


@fixture
def mock_message_service_stub(mocker: MockerFixture) -> Mock:
    """Mock out MessageServiceStub import in the config module."""
    mock_message_service_stub: Mock = mocker.patch(
        "bitfount.federated.transport.config.MessageServiceStub", autospec=True
    )
    return mock_message_service_stub


@fixture
def mock_message_service() -> Mock:
    """Returns a mocked message service."""
    mock_message_service: Mock = create_autospec(_MessageService, instance=True)
    return mock_message_service


@fixture
def mock_poll_for_messages(
    # this should be another fixture in the scope of the tests being run
    mock_message_service: Mock,
) -> Callable[[Iterable[MessageOrException]], AsyncIteratorMock]:
    """Returns a function that can be used to assign messages to yield."""

    def mocked_poll_for_messages(
        messages: Iterable[MessageOrException],
    ) -> AsyncIteratorMock:
        """Assigns an iterable of messages to the yield of poll_for_messages."""
        # Assign these to poll_for_messages which is the underlying method we
        # expect to yield messages.
        async_iterator = AsyncIteratorMock(messages)
        mock_message_service.poll_for_messages.return_value = async_iterator
        return async_iterator

    return mocked_poll_for_messages


@fixture
def rpc_error() -> RpcError:
    """Creates an RpcError exception to use in mocking error message retrieval."""
    # Create fake RpcError, manually set code method as valid RpcError can't
    # be created directly in Python code.
    rpc_error = RpcError()
    rpc_error.code = lambda: StatusCode.UNKNOWN  # type: ignore[assignment] # Reason: see comment # noqa: B950
    return rpc_error


@fixture
def mock_message_timestamps(mocker: MockerFixture) -> Callable[[Iterable[str]], Mock]:
    """Returns a callable that will mock out message_service._current_time.

    Each call to _current_time() will instead return the next string in the supplied
    iterable.
    """

    def _message_timestamp_mocker(fake_timestamps: Iterable[str]) -> Mock:
        # Because of how dataclass default_factory works, patching
        # message_service._current_time won't be sufficient as it's already bound
        # to the dataclass. Instead we have to patch out the inner calls to datetime.
        mock_datetime: Mock = mocker.patch(
            "bitfount.federated.transport.message_service.datetime", autospec=True
        )
        mock_datetime.now.return_value.isoformat.side_effect = fake_timestamps
        return mock_datetime

    return _message_timestamp_mocker
