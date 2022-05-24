from __future__ import annotations

import simplejson as json
from concurrent.futures import Executor, ThreadPoolExecutor, as_completed, wait
from datetime import datetime, timezone
from functools import partial
from gzip import GzipFile
from io import BytesIO
from queue import Empty, Queue
from requests import Session
from requests.models import PreparedRequest
from signal import SIGTERM, signal
from threading import Event, RLock, Thread
from time import sleep
from typing import TYPE_CHECKING, Any, BinaryIO, Generator, Union

import dynamic_function_loader
from aws_error_utils import catch_aws_error
from requests import post

from .. import (
    _GET_BULK_DATA_STORAGE_GQL,
    _GET_NODE_GQL,
    BatchItemFailures,
)
from .. import BulkDataStorage as BaseBulkDataStorage
from .. import Edge, LambdaEvent, LambdaSqsRecords, Message, MessageType
from .. import Node as BaseNode
from .. import getLogger

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import (
        DeleteMessageBatchRequestEntryTypeDef,
        SendMessageBatchRequestEntryTypeDef,
    )
else:
    DeleteMessageBatchRequestEntryTypeDef = dict
    SendMessageBatchRequestEntryTypeDef = dict


class _Queue(Queue):
    def tasks_done(self, count: int) -> None:
        with self.all_tasks_done:
            unfinished = self.unfinished_tasks - count
            if unfinished < 0:
                raise ValueError("count larger than unfinished tasks")
            if unfinished == 0:
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished


class _AuditRecordQueue(_Queue):
    def __init__(self, message_type: MessageType, node: Node) -> None:
        super().__init__()

        def cognito_auth(prepared_request: PreparedRequest) -> PreparedRequest:
            with node._lock:
                node._cognito.check_token()
            prepared_request.headers[
                "Authorization"
            ] = f"Bearer {node._cognito.access_token}"
            return prepared_request

        def sender() -> None:
            with Session() as session:
                while True:
                    batch: list[dict] = list()
                    while len(batch) < 500:
                        try:
                            batch.append(self.get(timeout=node.timeout))
                        except Empty:
                            break
                    if not batch:
                        continue
                    try:
                        session.post(
                            auth=cognito_auth,
                            json=dict(
                                messageType=message_type,
                                auditRecords=batch,
                            ),
                            url=f"{node._audit_records_endpoint}/{node.name}",
                        ).raise_for_status()
                    except Exception:
                        getLogger().exception("Error creating audit records")
                    finally:
                        self.tasks_done(len(batch))

        Thread(daemon=True, name=f"AuditRecordsSender", target=sender).start()

    def get(self, block: bool = True, timeout: float = None) -> dict:
        return super().get(block=block, timeout=timeout)


class _BulkDataStorage(BaseBulkDataStorage):
    def handle_bulk_data(self, data: Union[bytearray, bytes, BinaryIO]) -> str:
        if isinstance(data, BinaryIO):
            data = data.read()
        with BytesIO() as buffer:
            with GzipFile(mode="wb", fileobj=buffer) as gzf:
                gzf.write(data)
            buffer.seek(0)
            post(
                self.presigned_post.url,
                data=self.presigned_post.fields,
                files=dict(file=("bulk_data", buffer)),
            ).raise_for_status()
        return self.presigned_get


class _BulkDataStorageQueue(Queue):
    def __init__(self, node: Node) -> None:
        super().__init__()
        self.__fill = Event()

        def filler() -> None:
            while True:
                self.__fill.wait()
                try:
                    with node._lock:
                        with node._gql_client as session:
                            bulk_data_storages: list[dict] = session.execute(
                                _GET_BULK_DATA_STORAGE_GQL,
                                variable_values={
                                    "tenant": node.tenant,
                                    "useAccelerationEndpoint": node.bulk_data_acceleration,
                                },
                            )["GetBulkDataStorage"]
                except Exception:
                    getLogger().exception("Error getting bulk data storage")
                else:
                    for bulk_data_storage in bulk_data_storages:
                        self.put_nowait(_BulkDataStorage(bulk_data_storage))
                self.__fill.clear()

        Thread(daemon=True, name="BulkDataStorageQueueFiller", target=filler).start()

    def get(self, block: bool = True, timeout: float = None) -> _BulkDataStorage:
        if self.qsize() < 20:
            self.__fill.set()
        bulk_data_storage: _BulkDataStorage = super().get(block=block, timeout=timeout)
        return (
            bulk_data_storage
            if not bulk_data_storage.expired
            else self.get(block=block, timeout=timeout)
        )


class _TargetMessageQueue(_Queue):
    def __init__(self, node: Node, edge: Edge) -> None:
        super().__init__()

        def batcher() -> Generator[
            list[SendMessageBatchRequestEntryTypeDef],
            None,
            list[SendMessageBatchRequestEntryTypeDef],
        ]:
            batch: list[SendMessageBatchRequestEntryTypeDef] = list()
            batch_length = 0
            id = 0
            while True:
                try:
                    message = self.get(timeout=node.timeout)
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
                except Empty:
                    if batch:
                        yield batch
                    batch = list()
                    batch_length = 0
                    id = 0

        def sender() -> None:
            for entries in batcher():
                try:
                    response = node._sqs_client.send_message_batch(
                        Entries=entries, QueueUrl=edge.queue
                    )
                    for failed in response.get("Failed", list()):
                        id = failed.pop("Id")
                        getLogger().error(
                            f"Unable to send message {entries[id]} to {edge.name}, reason {failed}"
                        )
                except Exception:
                    getLogger().exception(f"Error sending messages to {edge.name}")
                finally:
                    self.tasks_done(len(entries))

        Thread(
            daemon=True, name=f"TargetMessageSender({edge.name})", target=sender
        ).start()

    def get(self, block: bool = True, timeout: float = None) -> Message:
        return super().get(block=block, timeout=timeout)


class Node(BaseNode):
    """
    Base class for all threading Nodes.
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
            name=name,
            password=password,
            tenant=tenant,
            timeout=timeout,
            user_pool_id=user_pool_id,
            username=username,
        )
        self.__bulk_data_storage_queue = _BulkDataStorageQueue(self)
        self.__audit_records_queues: dict[str, _AuditRecordQueue] = dict()
        self.__lock = RLock()
        self.__target_message_queues: dict[str, _TargetMessageQueue] = dict()

    @property
    def _lock(self) -> RLock:
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

    def handle_bulk_data(self, data: Union[bytearray, bytes]) -> str:
        """
        Posts data as bulk data and returns a GET URL for data retrieval.
        Normally this returned URL will be used as a "ticket" in messages
        that require bulk data.
        """
        return self.__bulk_data_storage_queue.get().handle_bulk_data(data)

    def handle_received_message(self, *, message: Message, source: str) -> None:
        """
        Callback called when a message is received. Subclasses that receive messages
        should override this method.
        """
        pass

    def join(self) -> None:
        """
        Joins the calling thread with this Node. Will block until all
        join conditions are satified.
        """
        for target_message_queue in self.__target_message_queues.values():
            target_message_queue.join()
        for audit_records_queue in self.__audit_records_queues.values():
            audit_records_queue.join()

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

    def start(self) -> None:
        """
        Starts this Node. Must be called prior to any other usage.
        """
        getLogger().info(f"Starting Node {self.name}")
        with self._lock:
            with self._gql_client as session:
                data: dict[str, Union[str, dict]] = session.execute(
                    _GET_NODE_GQL,
                    variable_values=dict(name=self.name, tenant=self.tenant),
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
            ] = _AuditRecordQueue(self._receive_message_type, self)
        if send_message_type := data.get("sendMessageType"):
            self._send_message_type = MessageType(
                auditor=dynamic_function_loader.load(send_message_type["auditor"]),
                name=send_message_type["name"],
            )
            self.__audit_records_queues[send_message_type["name"]] = _AuditRecordQueue(
                self._send_message_type, self
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

    def stop(self) -> None:
        """Stops the Node's processing."""
        pass


class _DeleteMessageQueue(_Queue):
    def __init__(self, edge: Edge, node: AppNode) -> None:
        super().__init__()

        def deleter() -> None:
            while True:
                receipt_handles: list[str] = list()
                while len(receipt_handles) < 10:
                    try:
                        receipt_handles.append(self.get(timeout=node.timeout))
                    except Empty:
                        break
                if not receipt_handles:
                    continue
                try:
                    response = node._sqs_client.delete_message_batch(
                        Entries=[
                            DeleteMessageBatchRequestEntryTypeDef(
                                Id=str(id), ReceiptHandle=receipt_handle
                            )
                            for id, receipt_handle in enumerate(receipt_handles)
                        ],
                        QueueUrl=edge.queue,
                    )
                    for failed in response.get("Failed", list()):
                        id = failed.pop("Id")
                        getLogger().error(
                            f"Unable to delete message {receipt_handles[id]} from {edge.name}, reason {failed}"
                        )
                except Exception:
                    getLogger().exception(f"Error deleting messages from {edge.name}")
                finally:
                    self.tasks_done(len(receipt_handles))

        Thread(
            daemon=True, name=f"SourceMessageDeleter({edge.name})", target=deleter
        ).start()

    def get(self, block: bool = True, timeout: float = None) -> str:
        return super().get(block=block, timeout=timeout)


class _SourceMessageReceiver(Thread):
    def __init__(self, edge: Edge, node: AppNode) -> None:
        self.__continue = Event()
        self.__continue.set()
        self.__delete_message_queue = _DeleteMessageQueue(edge, node)

        def handle_received_message(message: Message, receipt_handle: str) -> bool:
            try:
                node.handle_received_message(message=message, source=edge.name)
            except Exception:
                getLogger().exception(
                    f"Error handling recevied message for {edge.name}"
                )
                return False
            else:
                self.__delete_message_queue.put_nowait(receipt_handle)
            return True

        def receive() -> None:
            self.__continue.wait()
            getLogger().info(f"Receiving messages from {edge.name}")
            while self.__continue.is_set():
                try:
                    response = node._sqs_client.receive_message(
                        AttributeNames=["All"],
                        MaxNumberOfMessages=10,
                        MessageAttributeNames=["All"],
                        QueueUrl=edge.queue,
                        WaitTimeSeconds=20,
                    )
                except catch_aws_error("AWS.SimpleQueueService.NonExistentQueue"):
                    getLogger().warning(f"Queue {edge.queue} does not exist, exiting")
                    break
                except Exception:
                    getLogger().exception(
                        f"Error receiving messages from {edge.name}, retrying"
                    )
                    sleep(20)
                else:
                    if not (sqs_messages := response.get("Messages")):
                        continue
                    getLogger().info(f"Received {len(sqs_messages)} from {edge.name}")

                    message_handlers = [
                        partial(
                            handle_received_message,
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

                    def handle_received_messages() -> None:
                        if executor := node._executor:
                            wait(
                                [
                                    executor.submit(message_handler)
                                    for message_handler in message_handlers
                                ]
                            )
                        else:
                            for message_handler in message_handlers:
                                if not message_handler():
                                    break

                    Thread(
                        name="handle_received_messages",
                        target=handle_received_messages,
                    ).start()

            getLogger().info(f"Stopping receiving messages from {edge.name}")

        super().__init__(name=f"SourceMessageReceiver({edge.name})", target=receive)
        self.start()

    def join(self) -> None:
        super().join()
        self.__delete_message_queue.join()

    def stop(self) -> None:
        self.__continue.clear()


class AppNode(Node):
    """
    A daemon Node intended to be used as either a stand-alone application
    or as a part of a larger application.
    """

    def __init__(
        self,
        *,
        appsync_endpoint: str = None,
        bulk_data_acceleration: bool = False,
        client_id: str = None,
        executor: Executor = None,
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
        self.__executor = executor
        self.__source_message_receivers: list[_SourceMessageReceiver] = list()
        self.__stop = Event()

    @property
    def _executor(self) -> Executor:
        return self.__executor

    def join(self) -> None:
        """
        Method to join all the app node receivers so that main thread can wait for their execution to complete.
        """
        self.__stop.wait()
        for app_node_receiver in self.__source_message_receivers:
            app_node_receiver.join()
        super().join()

    def start(self) -> None:
        """
        Calls start of Node class
        """
        super().start()
        self.__stop.clear()
        self.__source_message_receivers = [
            _SourceMessageReceiver(edge, self) for edge in self._sources
        ]

    def start_and_run_forever(self) -> None:
        """Will start this Node and run until stop is called"""
        self.start()
        self.join()

    def stop(self) -> None:
        """
        Stops the Node gracefully
        """
        self.__stop.set()
        for app_node_receiver in self.__source_message_receivers:
            app_node_receiver.stop()


class LambdaNode(Node):
    """
    A Node class intended to be implemented in an AWS Lambda function.
    Nodes that inherit from this class are automatically started on
    creation.
    """

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
        self.start()
        signal(SIGTERM, self._shutdown_handler)
        self.__executor: Executor = (
            ThreadPoolExecutor() if concurrent_processing else None
        )
        self.__queue_name_to_source = {
            edge.queue.split("/")[-1:][0]: edge.name for edge in self._sources
        }
        self.__report_batch_item_failures = report_batch_item_failures

    def _get_source(self, queue_arn: str) -> str:
        return self.__queue_name_to_source[queue_arn.split(":")[-1:][0]]

    def _shutdown_handler(self, signum: int, _: object) -> None:
        getLogger().info("Received SIGTERM, shutting down")
        self.join()
        getLogger().info("Shutdown complete")

    def handle_event(self, event: LambdaEvent) -> BatchItemFailures:
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

        def handle_received_message(message: Message, message_id: str) -> None:
            try:
                self.handle_received_message(message=message, source=source)
            except Exception:
                if not self.__report_batch_item_failures:
                    raise
                getLogger().exception(f"Error handling recevied message for {source}")
            else:
                if self.__report_batch_item_failures:
                    batch_item_failures.remove(message_id)

        message_handlers = [
            partial(
                handle_received_message,
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

        if executor := self.__executor:
            for future in as_completed(
                [
                    executor.submit(message_handler)
                    for message_handler in message_handlers
                ]
            ):
                if exception := future.exception():
                    raise exception
        else:
            for message_handler in message_handlers:
                message_handler()
        self.join()
        if self.__report_batch_item_failures and batch_item_failures:
            return dict(
                batchItemFailures=[
                    dict(itemIdentifier=message_id)
                    for message_id in batch_item_failures
                ]
            )
