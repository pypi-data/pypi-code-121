"""File containing mock objects for the purposes of testing."""
from __future__ import annotations

from asyncio import Queue
from collections.abc import Awaitable
import dataclasses
import inspect
from inspect import Parameter
import logging
import multiprocessing
from multiprocessing.managers import SyncManager
import time
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Collection,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from unittest.mock import AsyncMockMixin, NonCallableMock, create_autospec

from grpc import RpcError, StatusCode
from typing_extensions import TypeAlias

from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
    _MessageService,
)
from bitfount.federated.transport.protos.messages_pb2 import (
    BitfountMessage as GrpcBitfountMessage,
)
from bitfount.federated.transport.protos.messages_pb2 import (
    BitfountTasks,
    BlobStorageData,
    CommunicationDetails,
    LargeStorageRequest,
    PodData,
    SuccessResponse,
)
from bitfount.federated.transport.protos.messages_pb2 import Acknowledgement
from bitfount.federated.transport.protos.messages_pb2_grpc import MessageServiceStub

logger = logging.getLogger(__name__)


class LocalMessageServiceSharedQueues:
    """Class that simulates message mailboxes with asyncio.Queues."""

    def __init__(self) -> None:
        """Create new LocalMessageServiceSharedQueues instance."""
        self._queues: Dict[str, Queue[_BitfountMessage]] = {}

    async def send_message(self, mailbox_id: str, message: _BitfountMessage) -> None:
        """Sends a message to the queue for mailbox_id."""
        await self._queues[mailbox_id].put(message)

    async def get_message(self, mailbox_id: str) -> _BitfountMessage:
        """Awaits on a message to pull from queue for mailbox_id."""
        return await self._queues[mailbox_id].get()

    def add_mailbox(self, mailbox_id: str) -> None:
        """Creates a new queue for mailbox_id."""
        self._queues[mailbox_id] = Queue()


class LocalMessageService(_MessageService):
    """A class that implements the MessageService using asyncio.Queues.

    Has the same interface as MessageService but is designed for local testing.
    """

    # noinspection PyMissingConstructor
    def __init__(
        self,
        username: str,
        shared_queues: LocalMessageServiceSharedQueues,
        modeller_mailbox_id: Optional[str] = None,
        pod_ids: Optional[Collection[str]] = None,
    ):
        """Create new LocalMessageService.

        Args:
            username: The username of the account "running" this message service.
            shared_queues: The shared queues to act as the mailboxes.
            modeller_mailbox_id: Optional. The modeller's mailbox ID to simulate with.
            pod_ids: Optional. The group of pod_ids to simulate with.
        """
        # We don't have a BitfountSession to keep track of username with, so we
        # need it manually.
        self._username = username
        self._shared_queues = shared_queues
        self._modeller_mailbox_id = modeller_mailbox_id
        self._pod_ids = pod_ids

    @property
    def username(self) -> str:
        """Username running this message service."""
        return self._username

    @property
    def modeller_mailbox_id(self) -> str:
        """The modeller_mailbox_id to use for this message service."""
        if self._modeller_mailbox_id:
            return self._modeller_mailbox_id
        else:
            raise ValueError("No modeller_mailbox_id set.")

    @property
    def worker_mailbox_ids(self) -> Dict[str, str]:
        """A mapping of pod identifiers to worker_mailbox_ids.

        Deterministically generated so that they can be accessed consistently
        across all LocalMessageService instances using the same queue backend.
        """
        if not self._pod_ids:
            raise ValueError("No worker_mailbox_ids set.")
        return {
            pod_identifier: self._get_worker_mailbox_id(pod_identifier)
            for pod_identifier in self._pod_ids
        }

    async def connect_pod(self, pod_name: str) -> str:
        """See parent for more information."""
        # TODO: [BIT-960] Currently this is just hardcoded to return the pod_name
        #       (which is what the mailbox ID will actually be). [BIT-960] will have
        #       the PodConnect method actually return the generated mailbox ID so
        #       that if the approach changes in future it only needs to change on
        #       the message service side. At that point this should return the
        #       generated mailbox ID instead.
        pod_mailbox_id = pod_name
        # Create queue for pod
        self._shared_queues.add_mailbox(pod_mailbox_id)
        return pod_mailbox_id

    async def setup_communication_with_pods(
        self, tasks_per_pod: Mapping[str, bytes]
    ) -> Tuple[str, Dict[str, str]]:
        """See parent for more information."""
        # Create queues for modeller and for workers
        self._shared_queues.add_mailbox(self.modeller_mailbox_id)

        for worker_mailbox_id in self.worker_mailbox_ids.values():
            self._shared_queues.add_mailbox(worker_mailbox_id)

        return self.modeller_mailbox_id, self.worker_mailbox_ids

    async def poll_for_messages(
        self, mailbox_id: str
    ) -> AsyncGenerator[_BitfountMessage, None]:
        """See parent for more information."""
        while True:
            yield await self._shared_queues.get_message(mailbox_id)

    async def send_message(
        self, message: _BitfountMessage, already_packed: bool = False
    ) -> SuccessResponse:
        """See parent for more information."""
        await self._shared_queues.send_message(message.recipient_mailbox_id, message)
        return create_autospec(SuccessResponse, instance=True)

    @staticmethod
    def _get_worker_mailbox_id(pod_identifier: str) -> str:
        """Deterministically generates a worker mailbox ID from a pod identifier."""
        return f"{pod_identifier}_worker"


class GRPCStubMock(MessageServiceStub):
    """Multiprocess friendly GRPC Stub Fake.

    This mocks the behaviour of the message service.
    It can handle a single training job.
    It assumes the happy path is followed, the only 'error' it handles is
    when no messages are available.
    """

    # noinspection PyMissingConstructor
    def __init__(
        self,
        tokens_to_usernames: Mapping[str, str],
        manager: SyncManager,
        get_message_timeout: float = 0.1,
    ):
        self.tokens_to_usernames = tokens_to_usernames
        self.manager = manager
        self.get_message_timeout = get_message_timeout
        self.queue_id_counter = manager.Value("i", 1)
        self.large_object_id_counter = manager.Value("i", 1)

        self.queues: Dict[str, List[GrpcBitfountMessage]] = manager.dict()

        self.lock = multiprocessing.Lock()

    @staticmethod
    def _get_token(metadata: Sequence[Tuple[str, str]]) -> str:
        """Retrieve token from metadata."""
        return metadata[0][1]

    async def PodConnect(
        self, data: PodData, metadata: Sequence[Tuple[str, Any]]
    ) -> SuccessResponse:
        """Fakes PodConnect behaviour."""
        pod_id = self.tokens_to_usernames[self._get_token(metadata)]
        pod_queue_name = pod_id.replace("/", "-")
        with self.lock:
            self.queues[pod_queue_name] = self.manager.list()

        return SuccessResponse()

    async def SetupTaskMailboxes(
        self, data: BitfountTasks, metadata: Sequence[Tuple[str, Any]]
    ) -> CommunicationDetails:
        """Fakes SetupTaskMailboxes behaviour."""
        modeller_name = self.tokens_to_usernames[self._get_token(metadata)]

        with self.lock:
            modeller_queue_id = self.queue_id_counter.value
            self.queues[
                f"{modeller_name}-{self.queue_id_counter.value}"
            ] = self.manager.list()
            self.queue_id_counter.value += 1

            pod_mailbox_ids = {}
            for task in data.tasks:
                print(f"Queues are: {self.queues}")
                namespace, name = task.podIdentifier.split("/")
                # Pod queue creation
                print(f"making queue: '{namespace}-{self.queue_id_counter.value}'")
                self.queues[
                    f"{namespace}-{self.queue_id_counter.value}"
                ] = self.manager.list()
                pod_mailbox_ids[task.podIdentifier] = str(self.queue_id_counter.value)
                self.queue_id_counter.value += 1

            for task in data.tasks:
                namespace, name = task.podIdentifier.split("/")
                general_mailbox_name = f"{namespace}-{name}"
                print(f"MOCK MAILBOXES: {pod_mailbox_ids}")
                self.queues[general_mailbox_name].append(
                    GrpcBitfountMessage(
                        messageType=_BitfountMessageType.JOB_REQUEST.value,
                        body=task.encryptedTask,
                        sender=modeller_name,
                        senderMailboxId=str(modeller_queue_id),
                        recipient=task.podIdentifier,
                        recipientMailboxId=general_mailbox_name,
                        podMailboxIds=pod_mailbox_ids,
                    )
                )

        print(f"POD MAILBOXES: {pod_mailbox_ids}")
        return CommunicationDetails(
            mailboxId=str(modeller_queue_id), podMailboxIds=pod_mailbox_ids
        )

    async def SendBitfountMessage(
        self, data: GrpcBitfountMessage, metadata: Sequence[Tuple[str, Any]]
    ) -> SuccessResponse:
        """Fakes SendBitfountMessage behaviour."""
        sender_name = self.tokens_to_usernames[self._get_token(metadata)]
        recipient_username = data.recipient

        if "/" in data.recipient:
            # It's for a pod
            recipient_username, pod_name = data.recipient.split("/")

        with self.lock:
            self.queues[f"{recipient_username}-{data.recipientMailboxId}"].append(
                GrpcBitfountMessage(
                    messageType=data.messageType,
                    body=data.body,
                    recipient=recipient_username,
                    recipientMailboxId=data.recipientMailboxId,
                    sender=sender_name,
                    senderMailboxId=data.senderMailboxId,
                )
            )
        return SuccessResponse()

    async def GetBitfountMessage(
        self, data: CommunicationDetails, metadata: Sequence[Tuple[str, Any]]
    ) -> GrpcBitfountMessage:
        """Fakes GetBitfountMessage behaviour."""
        user_name = self.tokens_to_usernames[self._get_token(metadata)]

        if "/" in user_name:
            # It's a pod, we need to split out the pod name from the username
            user_name = user_name.split("/")[0]

        self.lock.acquire()
        mailbox = self.queues[f"{user_name}-{data.mailboxId}"]

        if len(mailbox) == 0:
            self.lock.release()
            time.sleep(self.get_message_timeout)
            self.lock.acquire()

            if len(mailbox) == 0:
                self.lock.release()

                # Create an RpcError, manually setting the code property as this
                # class is normally constructed in C code.
                error = RpcError()
                error.code = lambda: StatusCode.NOT_FOUND  # type: ignore[assignment] # Reason: see comment # noqa: B950

                raise error

        message = mailbox[0]
        self.lock.release()

        return message

    async def AcknowledgeMessage(
        self, data: Acknowledgement, metadata: Sequence[Tuple[str, Any]]
    ) -> SuccessResponse:
        """Fakes AcknowledgeMessage behaviour."""
        user_name = self.tokens_to_usernames[self._get_token(metadata)]
        if "/" in user_name:
            # It's a pod, we need to split out the pod name from the username
            user_name = user_name.split("/")[0]

        with self.lock:
            self.queues[f"{user_name}-{data.mailboxId}"].pop(0)

        return SuccessResponse()

    async def GetLargeObjectStorage(
        self, data: LargeStorageRequest, metadata: Sequence[Tuple[str, Any]]
    ) -> BlobStorageData:
        """Get URLs for upload/download of a large message."""
        # Locking just to ensure that we have a unique counter value
        with self.lock:
            print(
                f"Large storage {self.large_object_id_counter.value} "
                f"taken by: {self.tokens_to_usernames[self._get_token(metadata)]} "
                f"(pod: {data.podName})"
            )
            result = BlobStorageData(
                uploadUrl=f"https://test-message-service-"
                f"external.s3.eu-west-2.amazonaws.com/"
                f"upload?large-object-id="
                f"{self.large_object_id_counter.value}",
                downloadUrl=f"https://test-message-service-"
                f"external.s3.eu-west-2.amazonaws.com/"
                f"download?large-object-id="
                f"{self.large_object_id_counter.value}",
                uploadFields={"key": "some/key", "bucket": "some-bucket"},
            )
            self.large_object_id_counter.value += 1
            return result


# Type var for AsyncIteratorMock
T = TypeVar("T")


class AsyncIteratorMock(AsyncIterator, Generic[T]):
    """A mocked async iterator that will iterate a sync iterable."""

    def __init__(self, iterable: Iterable[T]) -> None:
        self.iterator: Iterator[T] = iter(iterable)

    def __aiter__(self) -> AsyncIteratorMock[T]:
        return self

    async def __anext__(self) -> T:
        # Iterate through the iterable, raising exceptions if they are present
        try:
            result = next(self.iterator)
            if self._is_exception(result):
                raise cast(BaseException, result)
            return result
        except StopIteration:
            pass
        raise StopAsyncIteration

    @staticmethod
    def _is_exception(obj: Any) -> bool:
        return (
            isinstance(obj, BaseException)
            or isinstance(obj, type)
            and issubclass(obj, BaseException)
        )


DataclassMock: TypeAlias = NonCallableMock


def create_dataclass_mock(
    dataclass_cls_or_instance: Union[Any, Type[Any]]
) -> DataclassMock:
    """Creates a mock whose spec matches the attributes of target dataclass.

    The actual mock is a NonCallableMock instance as it makes no sense to call
    a dataclass instance.
    """
    if not dataclasses.is_dataclass(dataclass_cls_or_instance):
        raise TypeError("create_dataclass_mock should only be used on dataclasses.")

    # To force create_autospec to find all the attributes (including those that
    # don't have default values) we need to instantiate a dataclass instance to
    # get everything set. If we already have an instance this is fine, otherwise
    # we need to work out (and pass) the number of expected args.
    dataclass_instance: Any
    if inspect.isclass(dataclass_cls_or_instance):
        # Work out and create instance from class
        dataclass_cls: Type[Any] = dataclass_cls_or_instance
        sig = inspect.signature(dataclass_cls)
        params = sig.parameters.values()
        # Find params that _can_ be supplied positionally
        args = [
            p
            for p in params
            if p.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
        ]
        # Find params that don't have default values (Parameter.empty denotes no
        # default value)
        needed_args = [p for p in args if p.default == Parameter.empty]
        false_args = [None] * len(needed_args)
        dataclass_instance = dataclass_cls(*false_args)
    else:
        # Use instance directly
        dataclass_instance = cast(Any, dataclass_cls_or_instance)

    dataclass_mock: DataclassMock = create_autospec(
        spec=dataclass_instance, instance=True
    )

    return dataclass_mock


class AwaitableMock(AsyncMockMixin, NonCallableMock, Awaitable):
    """A non-callable async mock which is also directly awaitable.

    Useful for mocking out things like Task or Future instances.

    It implements __await__ to yield and return `None` (which gets around
    compatibility issues with asyncio not being able to await a Mock subclass
    directly) and to record the call to __await__.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def __await__(self) -> Generator[None, None, None]:
        self.await_count += 1
        yield None
