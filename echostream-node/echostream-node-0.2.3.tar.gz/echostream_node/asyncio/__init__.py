from __future__ import annotations

import asyncio
import threading
from datetime import datetime, timezone
from functools import partial
from gzip import GzipFile
from io import BytesIO
from typing import TYPE_CHECKING, Any, AsyncGenerator, BinaryIO, Union

import aiorun
import dynamic_function_loader
import simplejson as json
import uvloop
from aiohttp import ClientSession, FormData
from aws_error_utils import catch_aws_error
from gql.transport.aiohttp import AIOHTTPTransport
from pycognito import Cognito

from .. import (
    _GET_BULK_DATA_STORAGE_GQL,
    _GET_NODE_GQL,
    BatchItemFailures,
)
from .. import BulkDataStorage as BaseBulkDataStorage
from .. import Edge, LambdaEvent, LambdaSqsRecords, Message, MessageType
from .. import Node as BaseNode
from .. import PresignedPost, getLogger

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import (
        DeleteMessageBatchRequestEntryTypeDef,
        SendMessageBatchRequestEntryTypeDef,
    )
else:
    DeleteMessageBatchRequestEntryTypeDef = dict
    SendMessageBatchRequestEntryTypeDef = dict


class _AuditRecordQueue(asyncio.Queue):
    def __init__(self, message_type: MessageType, node: Node) -> None:
        super().__init__()

        async def cognito_auth() -> dict[str, str]:
            async with node._lock:
                node._cognito.check_token()
            return dict(Authorization=f"Bearer {node._cognito.access_token}")

        async def sender() -> None:
            cancelled = asyncio.Event()

            async def batcher() -> AsyncGenerator[
                list[dict],
                None,
            ]:
                batch: list[dict] = list()
                while not (cancelled.is_set() and self.empty()):
                    try:
                        try:
                            batch.append(
                                await asyncio.wait_for(self.get(), timeout=node.timeout)
                            )
                        except asyncio.TimeoutError:
                            if batch:
                                yield batch
                                batch = list()
                        else:
                            if len(batch) == 500:
                                yield batch
                                batch = list()
                    except asyncio.CancelledError:
                        cancelled.set()
                        if batch:
                            yield batch
                            batch = list()

            async with ClientSession() as session:
                async for batch in batcher():
                    async with node._lock:
                        node._cognito.check_token()
                    try:
                        async with session.post(
                            headers=await cognito_auth(),
                            json=dict(
                                messageType=message_type,
                                auditRecords=batch,
                            ),
                            url=f"{node._audit_records_endpoint}/{node.name}",
                        ) as response:
                            response.raise_for_status()
                    except asyncio.CancelledError:
                        cancelled.set()
                    except Exception:
                        getLogger().exception("Error creating audit records")
                    finally:
                        for _ in range(len(batch)):
                            self.task_done()

        asyncio.create_task(sender(), name=f"AuditRecordsSender")

    async def get(self) -> dict:
        return await super().get()


class _BulkDataStorage(BaseBulkDataStorage):
    def __init__(
        self,
        bulk_data_storage: dict[str, Union[str, PresignedPost]],
        session: ClientSession,
    ) -> None:
        super().__init__(bulk_data_storage)
        self.__client_session = session

    async def handle_bulk_data(self, data: Union[bytearray, bytes, BinaryIO]) -> str:
        if isinstance(data, BinaryIO):
            data = data.read()
        with BytesIO() as buffer:
            with GzipFile(mode="wb", fileobj=buffer) as gzf:
                gzf.write(data)
            buffer.seek(0)
            form_data = FormData(self.presigned_post.fields)
            form_data.add_field("file", buffer, filename="bulk_data")
            async with self.__client_session.post(
                data=form_data, url=self.presigned_post.url
            ) as response:
                response.raise_for_status()
        return self.presigned_get


class _BulkDataStorageQueue(asyncio.Queue):
    def __init__(self, node: Node) -> None:
        super().__init__()
        self.__fill = asyncio.Event()

        async def filler() -> None:
            async with ClientSession() as client_session:
                cancelled = asyncio.Event()
                while not cancelled.is_set():
                    bulk_data_storages: list[dict] = list()
                    try:
                        await self.__fill.wait()
                        async with node._lock:
                            async with node._gql_client as session:
                                bulk_data_storages = (
                                    await session.execute(
                                        _GET_BULK_DATA_STORAGE_GQL,
                                        variable_values={
                                            "tenant": node.tenant,
                                            "useAccelerationEndpoint": node.bulk_data_acceleration,
                                        },
                                    )
                                )["GetBulkDataStorage"]
                    except asyncio.CancelledError:
                        cancelled.set()
                    except Exception:
                        getLogger().exception("Error getting bulk data storage")
                    for bulk_data_storage in bulk_data_storages:
                        self.put_nowait(
                            _BulkDataStorage(bulk_data_storage, client_session)
                        )
                    self.__fill.clear()

        asyncio.create_task(filler(), name="BulkDataStorageQueueFiller")

    async def get(self) -> _BulkDataStorage:
        if self.qsize() < 20:
            self.__fill.set()
        bulk_data_storage: _BulkDataStorage = await super().get()
        return bulk_data_storage if not bulk_data_storage.expired else await self.get()


class _TargetMessageQueue(asyncio.Queue):
    def __init__(self, node: Node, edge: Edge) -> None:
        super().__init__()

        async def sender() -> None:
            cancelled = asyncio.Event()

            async def batcher() -> AsyncGenerator[
                list[SendMessageBatchRequestEntryTypeDef], None
            ]:
                batch: list[SendMessageBatchRequestEntryTypeDef] = list()
                batch_length = 0
                id = 0
                while not (cancelled.is_set() and self.empty()):
                    try:
                        try:
                            message = await asyncio.wait_for(
                                self.get(), timeout=node.timeout
                            )
                        except asyncio.TimeoutError:
                            if batch:
                                yield batch
                            batch = list()
                            batch_length = 0
                            id = 0
                        else:
                            if batch_length + len(message) > 262144:
                                yield batch
                                batch = list()
                                batch_length = 0
                                id = 0
                            batch.append(
                                SendMessageBatchRequestEntryTypeDef(
                                    Id=str(id), **message._sqs_message(node)
                                )
                            )
                            if len(batch) == 10:
                                yield batch
                                batch = list()
                                batch_length = 0
                                id = 0
                            id += 1
                            batch_length += len(message)
                    except asyncio.CancelledError:
                        cancelled.set()
                        if batch:
                            yield batch
                        batch = list()
                        batch_length = 0
                        id = 0

            async for entries in batcher():
                try:
                    response = await asyncio.get_running_loop().run_in_executor(
                        None,
                        partial(
                            node._sqs_client.send_message_batch,
                            Entries=entries,
                            QueueUrl=edge.queue,
                        ),
                    )
                except asyncio.CancelledError:
                    cancelled.set()
                except Exception:
                    getLogger().exception(f"Error sending messages to {edge.name}")
                finally:
                    for failed in response.get("Failed", list()):
                        id = failed.pop("Id")
                        getLogger().error(
                            f"Unable to send message {entries[id]} to {edge.name}, reason {failed}"
                        )
                    for _ in range(len(entries)):
                        self.task_done()

        asyncio.create_task(sender(), name=f"TargetMessageSender({edge.name})")

    async def get(self) -> Message:
        return await super().get()


class CognitoAIOHTTPTransport(AIOHTTPTransport):
    def __init__(self, cognito: Cognito, url: str, **kwargs: Any) -> None:
        self._cognito = cognito
        super().__init__(url, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        if name == "headers":
            self._cognito.check_token()
            return dict(Authorization=self._cognito.access_token)
        return super().__getattribute__(name)


class Node(BaseNode):
    """
    Base class for all implemented asyncio Nodes.

    Nodes of this class must be instantiated outside of
    the asyncio event loop.
    """

    def __init__(
        self,
        *,
        appsync_endpoint: str = None,
        bulk_data_acceleration: bool = False,
        client_id: str = None,
        name: str = None,
        password: str = None,
        tenant: str = None,
        timeout: float = None,
        user_pool_id: str = None,
        username: str = None,
    ) -> None:
        super().__init__(
            appsync_endpoint=appsync_endpoint,
            bulk_data_acceleration=bulk_data_acceleration,
            client_id=client_id,
            gql_transport_cls=CognitoAIOHTTPTransport,
            name=name,
            password=password,
            tenant=tenant,
            timeout=timeout,
            user_pool_id=user_pool_id,
            username=username,
        )
        self.__audit_records_queues: dict[str, _AuditRecordQueue] = dict()
        self.__bulk_data_storage_queue: _BulkDataStorageQueue = None
        self.__lock: asyncio.Lock = None
        self.__target_message_queues: dict[str, _TargetMessageQueue] = dict()

    @property
    def _lock(self) -> asyncio.Lock:
        return self.__lock

    def audit_message(
        self,
        /,
        message: Message,
        *,
        extra_attributes: dict[str, Any] = None,
        source: str = None,
    ) -> None:
        """
        Audits the provided message. If extra_attibutes is
        supplied, they will be added to the message's audit
        dict. If source is provided, it will be recorded in
        the audit.
        """
        extra_attributes = extra_attributes or dict()
        message_type = message.message_type
        record = dict(
            datetime=datetime.now(timezone.utc).isoformat(),
            previousTrackingIds=message.previous_tracking_ids,
            sourceNode=source,
            trackingId=message.tracking_id,
        )
        if attributes := (
            message_type.auditor(message=message.body) | extra_attributes
        ):
            record["attributes"] = json.dumps(attributes, separators=(",", ":"))
        try:
            self.__audit_records_queues[message_type.name].put_nowait(record)
        except KeyError:
            raise ValueError(f"Unrecognized message type {message_type.name}")

    def audit_messages(
        self,
        /,
        messages: list[Message],
        *,
        extra_attributes: list[dict[str, Any]] = None,
        source: str = None,
    ) -> None:
        """
        Audits the provided messages. If extra_attibutes is
        supplied they will be added to the respective message's audit
        dict and they must have the same count as messages.
        If source is provided, it will be recorded in the audit.
        """
        if extra_attributes and len(extra_attributes) != len(messages):
            raise ValueError(
                "messages and extra_attributes must have the same number of items"
            )
        for message, attributes in zip(messages, extra_attributes):
            self.audit_message(message, extra_attributes=attributes, source=source)

    async def handle_bulk_data(self, data: Union[bytearray, bytes]) -> str:
        """
        Posts data as bulk data and returns a GET URL for data retrieval.
        Normally this returned URL will be used as a "ticket" in messages
        that require bulk data.
        """
        return await (await self.__bulk_data_storage_queue.get()).handle_bulk_data(data)

    async def handle_received_message(self, *, message: Message, source: str) -> None:
        """
        Callback called when a message is received. Subclasses that receive messages
        should override this method.
        """
        pass

    async def join(self) -> None:
        """
        Joins the calling thread with this Node. Will block until all
        join conditions are satified.
        """
        await asyncio.gather(
            *[
                target_message_queue.join()
                for target_message_queue in self.__target_message_queues.values()
            ],
            *[
                audit_records_queue.join()
                for audit_records_queue in self.__audit_records_queues.values()
            ],
        )

    def send_message(self, /, message: Message, *, targets: set[Edge] = None) -> None:
        """
        Send the message to the specified targets. If no targets are specified
        the message will be sent to all targets.
        """
        self.send_messages([message], targets=targets)

    def send_messages(
        self, /, messages: list[Message], *, targets: set[Edge] = None
    ) -> None:
        """
        Send the messages to the specified targets. If no targets are specified
        the messages will be sent to all targets.
        """
        if messages:
            for target in targets or self.targets:
                if target_message_queue := self.__target_message_queues.get(
                    target.name
                ):
                    for message in messages:
                        target_message_queue.put_nowait(message)
                else:
                    getLogger().warning(f"Target {target.name} does not exist")

    async def start(self) -> None:
        """
        Starts this Node. Must be called prior to any other usage.
        """
        getLogger().info(f"Starting Node {self.name}")
        self.__lock = asyncio.Lock()
        self.__bulk_data_storage_queue = _BulkDataStorageQueue(self)
        async with self.__lock:
            async with self._gql_client as session:
                data: dict[str, Union[str, dict]] = (
                    await session.execute(
                        _GET_NODE_GQL,
                        variable_values=dict(name=self.name, tenant=self.tenant),
                    )
                )["GetNode"]
        self.config = (
            json.loads(data["tenant"].get("config") or "{}")
            | json.loads((data.get("app") or dict()).get("config") or "{}")
            | json.loads(data.get("config") or "{}")
        )
        if receive_message_type := data.get("receiveMessageType"):
            self._receive_message_type = MessageType(
                auditor=dynamic_function_loader.load(receive_message_type["auditor"]),
                name=receive_message_type["name"],
            )
            self.__audit_records_queues[
                receive_message_type["name"]
            ] = _AuditRecordQueue(self.receive_message_type, self)
        if send_message_type := data.get("sendMessageType"):
            self._send_message_type = MessageType(
                auditor=dynamic_function_loader.load(send_message_type["auditor"]),
                name=send_message_type["name"],
            )
            self.__audit_records_queues[send_message_type["name"]] = _AuditRecordQueue(
                self.send_message_type, self
            )
        if self.node_type == "AppChangeReceiverNode":
            if edge := data.get("receiveEdge"):
                self._sources = {Edge(name=edge["source"]["name"], queue=edge["queue"])}
            else:
                self._sources = set()
        else:
            self._sources = {
                Edge(name=edge["source"]["name"], queue=edge["queue"])
                for edge in (data.get("receiveEdges") or list())
            }
        self._targets = {
            Edge(name=edge["target"]["name"], queue=edge["queue"])
            for edge in (data.get("sendEdges") or list())
        }
        self.__target_message_queues = {
            edge.name: _TargetMessageQueue(self, edge) for edge in self._targets
        }


class _DeleteMessageQueue(asyncio.Queue):
    def __init__(self, edge: Edge, node: AppNode) -> None:
        super().__init__()

        async def deleter() -> None:
            cancelled = asyncio.Event()

            async def batcher() -> AsyncGenerator[
                list[str],
                None,
            ]:
                batch: list[str] = list()
                while not (cancelled.is_set() and self.empty()):
                    try:
                        try:
                            batch.append(
                                await asyncio.wait_for(self.get(), timeout=node.timeout)
                            )
                        except asyncio.TimeoutError:
                            if batch:
                                yield batch
                                batch = list()
                        else:
                            if len(batch) == 10:
                                yield batch
                                batch = list()
                    except asyncio.CancelledError:
                        cancelled.set()
                        if batch:
                            yield batch
                            batch = list()

            async for receipt_handles in batcher():
                try:
                    response = await asyncio.get_running_loop().run_in_executor(
                        None,
                        partial(
                            node._sqs_client.delete_message_batch,
                            Entries=[
                                DeleteMessageBatchRequestEntryTypeDef(
                                    Id=str(id), ReceiptHandle=receipt_handle
                                )
                                for id, receipt_handle in enumerate(receipt_handles)
                            ],
                            QueueUrl=edge.queue,
                        ),
                    )
                except asyncio.CancelledError:
                    cancelled.set()
                except Exception:
                    getLogger().exception(f"Error deleting messages from {edge.name}")
                finally:
                    for failed in response.get("Failed", list()):
                        id = failed.pop("Id")
                        getLogger().error(
                            f"Unable to delete message {receipt_handles[id]} from {edge.name}, reason {failed}"
                        )
                    for _ in range(len(receipt_handles)):
                        self.task_done()

        asyncio.create_task(deleter(), name=f"SourceMessageDeleter({edge.name})")

    async def get(self) -> str:
        return await super().get()


class _SourceMessageReceiver:
    def __init__(self, edge: Edge, node: AppNode) -> None:
        self.__delete_message_queue = _DeleteMessageQueue(edge, node)

        async def handle_received_message(
            message: Message, receipt_handle: str
        ) -> bool:
            try:
                await node.handle_received_message(message=message, source=edge.name)
            except asyncio.CancelledError:
                raise
            except Exception:
                getLogger().exception(
                    f"Error handling recevied message for {edge.name}"
                )
                return False
            else:
                self.__delete_message_queue.put_nowait(receipt_handle)
            return True

        async def receive() -> None:
            getLogger().info(f"Receiving messages from {edge.name}")
            while True:
                try:
                    response = await asyncio.get_running_loop().run_in_executor(
                        None,
                        partial(
                            node._sqs_client.receive_message,
                            AttributeNames=["All"],
                            MaxNumberOfMessages=10,
                            MessageAttributeNames=["All"],
                            QueueUrl=edge.queue,
                            WaitTimeSeconds=20,
                        ),
                    )
                except asyncio.CancelledError:
                    raise
                except catch_aws_error("AWS.SimpleQueueService.NonExistentQueue"):
                    getLogger().warning(f"Queue {edge.queue} does not exist, exiting")
                    break
                except Exception:
                    getLogger().exception(
                        f"Error receiving messages from {edge.name}, retrying"
                    )
                    await asyncio.sleep(20)
                else:
                    if not (sqs_messages := response.get("Messages")):
                        continue
                    getLogger().info(f"Received {len(sqs_messages)} from {edge.name}")

                    message_handlers = [
                        handle_received_message(
                            Message(
                                body=sqs_message["Body"],
                                group_id=sqs_message["Attributes"]["MessageGroupId"],
                                message_type=node.receive_message_type,
                                tracking_id=sqs_message["MessageAttributes"]
                                .get("trackingId", {})
                                .get("StringValue"),
                                previous_tracking_ids=sqs_message["MessageAttributes"]
                                .get("prevTrackingIds", {})
                                .get("StringValue"),
                            ),
                            sqs_message["ReceiptHandle"],
                        )
                        for sqs_message in sqs_messages
                    ]

                    async def handle_received_messages() -> None:
                        if node._concurrent_processing:
                            await asyncio.gather(*message_handlers)
                        else:
                            for message_handler in message_handlers:
                                if not await message_handler:
                                    break

                    asyncio.create_task(
                        handle_received_messages(), name="handle_received_messages"
                    )

            getLogger().info(f"Stopping receiving messages from {edge.name}")

        self.__task = asyncio.create_task(
            receive(), name=f"SourceMessageReceiver({edge.name})"
        )

    async def join(self) -> None:
        await asyncio.wait([self.__task])
        await self.__delete_message_queue.join()


class AppNode(Node):
    def __init__(
        self,
        *,
        appsync_endpoint: str = None,
        bulk_data_acceleration: bool = False,
        client_id: str = None,
        concurrent_processing: bool = False,
        name: str = None,
        password: str = None,
        tenant: str = None,
        timeout: float = None,
        user_pool_id: str = None,
        username: str = None,
    ) -> None:
        super().__init__(
            appsync_endpoint=appsync_endpoint,
            bulk_data_acceleration=bulk_data_acceleration,
            client_id=client_id,
            name=name,
            password=password,
            tenant=tenant,
            timeout=timeout,
            user_pool_id=user_pool_id,
            username=username,
        )
        self.__concurrent_processing = concurrent_processing
        self.__source_message_receivers: list[_SourceMessageReceiver] = list()

    @property
    def _concurrent_processing(self) -> bool:
        return self.__concurrent_processing

    async def join(self) -> None:
        """
        Joins the calling thread with this Node. Will block until all
        join conditions are satified.
        """
        await asyncio.gather(
            *[
                source_message_receiver.join()
                for source_message_receiver in self.__source_message_receivers
            ]
        )
        await super().join()

    async def start(self) -> None:
        """
        Starts this Node. Must be called prior to any other usage.
        """
        await super().start()
        self.__source_message_receivers = [
            _SourceMessageReceiver(edge, self) for edge in self._sources
        ]

    async def start_and_run_forever(self) -> None:
        """Will start this Node and run until the containing Task is cancelled"""
        await self.start()
        await self.join()


class LambdaNode(Node):
    def __init__(
        self,
        *,
        appsync_endpoint: str = None,
        bulk_data_acceleration: bool = False,
        client_id: str = None,
        concurrent_processing: bool = False,
        name: str = None,
        password: str = None,
        report_batch_item_failures: bool = False,
        tenant: str = None,
        timeout: float = None,
        user_pool_id: str = None,
        username: str = None,
    ) -> None:
        super().__init__(
            appsync_endpoint=appsync_endpoint,
            bulk_data_acceleration=bulk_data_acceleration,
            client_id=client_id,
            name=name,
            password=password,
            tenant=tenant,
            timeout=timeout or 0.01,
            user_pool_id=user_pool_id,
            username=username,
        )
        self.__concurrent_processing = concurrent_processing
        self.__loop: asyncio.AbstractEventLoop = None
        self.__queue_name_to_source = {
            edge.queue.split("/")[-1:][0]: edge.name for edge in self._sources
        }
        self.__report_batch_item_failures = report_batch_item_failures

        started = threading.Event()

        async def start_and_run_forever() -> None:
            try:
                await self.start()
                started.set()
                try:
                    # Sleep until cancelled by aiorun
                    while True:
                        await asyncio.sleep(86400)
                except asyncio.CancelledError:
                    pass
                await self.join()
            except asyncio.CancelledError:
                pass

        def event_loop():
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            self.__loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.__loop)
            aiorun.run(
                start_and_run_forever(), loop=self.__loop, stop_on_unhandled_errors=True
            )

        # Run the event loop in a seperate thread, or else we will block the main
        # Lambda execution!
        threading.Thread(name="event_loop", target=event_loop)
        # Wait until the started event is set before returning control to
        # Lambda
        started.wait()

    def _get_source(self, queue_arn: str) -> str:
        return self.__queue_name_to_source[queue_arn.split(":")[-1:][0]]

    async def _handle_event(self, event: LambdaEvent) -> BatchItemFailures:
        """
        Handles the AWS Lambda event passed into the containing
        AWS Lambda function during invocation.

        This is intended to be the only called method in your
        containing AWS Lambda function.
        """
        records: LambdaSqsRecords = None
        if not (records := event.get("Records")):
            getLogger().warning(f"No Records found in event {event}")
            return

        source = self._get_source(records[0]["eventSourceARN"])
        getLogger().info(f"Received {len(records)} messages from {source}")
        batch_item_failures: list[str] = (
            [record["messageId"] for record in records]
            if self.__report_batch_item_failures
            else None
        )

        async def handle_received_message(message: Message, message_id: str) -> None:
            try:
                await self.handle_received_message(message=message, source=source)
            except asyncio.CancelledError:
                raise
            except Exception:
                if not self.__report_batch_item_failures:
                    raise
                getLogger().exception(f"Error handling recevied message for {source}")
            else:
                if self.__report_batch_item_failures:
                    batch_item_failures.remove(message_id)

        message_handlers = [
            handle_received_message(
                Message(
                    body=record["body"],
                    group_id=record["attributes"]["MessageGroupId"],
                    message_type=self.receive_message_type,
                    previous_tracking_ids=record["messageAttributes"]
                    .get("prevTrackingIds", {})
                    .get("stringValue"),
                    tracking_id=record["messageAttributes"]
                    .get("trackingId", {})
                    .get("stringValue"),
                ),
                record["messageId"],
            )
            for record in records
        ]

        if self.__concurrent_processing:
            await asyncio.gather(*message_handlers)
        else:
            for message_handler in message_handlers:
                await message_handler()
        await self.join()
        if self.__report_batch_item_failures and batch_item_failures:
            return dict(
                batchItemFailures=[
                    dict(itemIdentifier=message_id)
                    for message_id in batch_item_failures
                ]
            )

    def handle_event(self, event: LambdaEvent) -> BatchItemFailures:
        return asyncio.run_coroutine_threadsafe(
            self._handle_event(event), self.__loop
        ).result()
