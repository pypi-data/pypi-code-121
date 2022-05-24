from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from os import cpu_count, environ
from threading import RLock
from time import time
from typing import TYPE_CHECKING, Any, Callable, Union
from uuid import uuid4

import awsserviceendpoints
import simplejson as json
from boto3.session import Session
from botocore.config import Config
from botocore.credentials import DeferredRefreshableCredentials
from botocore.session import Session as BotocoreSession
from gql import Client as GqlClient
from gql import gql
from gql.transport.requests import RequestsHTTPTransport
from pycognito import Cognito


def getLogger() -> logging.Logger:
    """
    Returns "echostream-node" logger
    """
    return logging.getLogger("echostream-node")


getLogger().addHandler(logging.NullHandler())

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_sqs.client import SQSClient
    from mypy_boto3_sqs.type_defs import MessageAttributeValueTypeDef
else:
    MessageAttributeValueTypeDef = dict
    SQSClient = object
    Table = object

_GET_APP_GQL = gql(
    """
    query getNode($name: String!, $tenant: String!) {
        GetNode(name: $name, tenant: $tenant) {
            __typename
            ... on AppChangeReceiverNode {
                app {
                    __typename
                    ... on CrossAccountApp {
                        auditRecordsEndpoint
                        name
                        tableAccess
                    }
                    ... on ExternalApp {
                        auditRecordsEndpoint
                        name
                        tableAccess
                    }
                    ... on ManagedApp {
                        auditRecordsEndpoint
                        name
                        tableAccess
                    }
                }
            }
            ... on ExternalNode {
                app {
                    __typename
                    ... on CrossAccountApp {
                        auditRecordsEndpoint
                        name
                        tableAccess
                    }
                    ... on ExternalApp {
                        auditRecordsEndpoint
                        name
                        tableAccess
                    }
                }
            }
            ... on ManagedNode {
                app {
                    __typename
                    auditRecordsEndpoint
                    name
                    tableAccess
                }
            }
            tenant {
                region
                table
            }
        }
    }
    """
)

_GET_AWS_CREDENTIALS_GQL = gql(
    """
    query getAppAwsCredentials($name: String!, $tenant: String!, $duration: Int!) {
        GetApp(name: $name, tenant: $tenant) {
            ... on ExternalApp {
                GetAwsCredentials(duration: $duration) {
                    accessKeyId
                    secretAccessKey
                    sessionToken
                    expiration
                }
            }
            ... on ManagedApp {
                GetAwsCredentials(duration: $duration) {
                    accessKeyId
                    secretAccessKey
                    sessionToken
                    expiration
                }
            }
        }
    }
    """
)

_GET_BULK_DATA_STORAGE_GQL = gql(
    """
    query getBulkDataStorage($tenant: String!, $useAccelerationEndpoint: Boolean!) {
        GetBulkDataStorage(tenant: $tenant, count: 20, useAccelerationEndpoint: $useAccelerationEndpoint) {
            expiration
            presignedGet
            presignedPost {
                fields
                url
            }
            presignedPut {
                headers
                url
            }
        }
    }
    """
)

_GET_NODE_GQL = gql(
    """
    query getNode($name: String!, $tenant: String!) {
        GetNode(name: $name, tenant: $tenant) {
            ... on AppChangeReceiverNode {
                receiveEdge {
                    queue
                    source {
                        name
                    }
                }
                receiveMessageType {
                    auditor
                    name
                }
            }
            ... on ExternalNode {
                app {
                    ... on CrossAccountApp {
                        config
                    }
                    ... on ExternalApp {
                        config
                    }
                }
                config
                receiveEdges {
                    queue
                    source {
                        name
                    }
                }
                receiveMessageType {
                    auditor
                    name
                }
                sendEdges {
                    queue
                    target {
                        name
                    }
                }
                sendMessageType {
                    auditor
                    name
                }
            }
            ... on ManagedNode {
                app {
                    config
                }
                config
                receiveEdges {
                    queue
                    source {
                        name
                    }
                }
                receiveMessageType {
                    auditor
                    name
                }
                sendEdges {
                    queue
                    target {
                        name
                    }
                }
                sendMessageType {
                    auditor
                    name
                }
            }
            tenant {
                config
            }
        }
    }
    """
)


class _NodeBotocoreSession(BotocoreSession):
    def __init__(
        self, *, node: Node, gql_client: GqlClient, duration: int = None
    ) -> None:
        super().__init__()
        lock = RLock()

        def refresher():
            with lock:
                with gql_client as session:
                    credentials = session.execute(
                        _GET_AWS_CREDENTIALS_GQL,
                        variable_values=dict(
                            name=node.app, tenant=node.tenant, duration=duration or 3600
                        ),
                    )["GetApp"]["GetAwsCredentials"]
            return dict(
                access_key=credentials["accessKeyId"],
                expiry_time=credentials["expiration"],
                secret_key=credentials["secretAccessKey"],
                token=credentials["sessionToken"],
            )

        setattr(
            self,
            "_credentials",
            DeferredRefreshableCredentials(
                method="GetApp.GetAwsCredentials", refresh_using=refresher
            ),
        )


Auditor = Callable[..., dict[str, Any]]
"""Typing for MessageType auditor functions"""

BatchItemFailures = dict[str, list[dict[str, str]]]


@dataclass(frozen=True, init=False)
class BulkDataStorage:
    """
    Class to manage bulk data storage.
    """

    expiration: int
    """Epoch, in seconds, when this expires"""
    presigned_get: str
    """URL that you can HTTP 'GET' to retrieve the bulk data"""
    presigned_post: PresignedPost
    """URL that you can HTTP 'POST' bulk data to, along with the fields the 'POST' requires"""
    presigned_put: PresignedPut
    """URL that you can HTTP 'PUT' bulk data to, along with the headers the 'PUT' requires"""

    def __init__(self, bulk_data_storage: dict[str, Union[str, PresignedPost]]) -> None:
        super().__init__()
        super().__setattr__("expiration", bulk_data_storage["expiration"])
        super().__setattr__("presigned_get", bulk_data_storage["presignedGet"])
        super().__setattr__(
            "presigned_post",
            PresignedPost(
                fields=json.loads(bulk_data_storage["presignedPost"]["fields"]),
                url=bulk_data_storage["presignedPost"]["url"],
            ),
        )
        super().__setattr__(
            "presigned_put",
            PresignedPut(
                headers=json.loads(bulk_data_storage["presignedPut"]["headers"]),
                url=bulk_data_storage["presignedPut"]["url"],
            ),
        )

    @property
    def expired(self) -> bool:
        """
        Returns False if presigned_post is expired.
        """
        return self.expiration < time()


class CognitoRequestsHTTPTransport(RequestsHTTPTransport):
    def __init__(self, cognito: Cognito, url: str, **kwargs: Any) -> None:
        self._cognito = cognito
        super().__init__(url, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        if name == "headers":
            self._cognito.check_token()
            return dict(Authorization=self._cognito.access_token)
        return super().__getattribute__(name)


@dataclass(frozen=True)
class Edge:
    """
    Edge dataclass to manage edge details.
    """

    name: str
    """The name of the Edge, normally the other end of the Edge"""
    queue: str
    """The SQS Queue URL of the Edge"""


LambdaEvent = Union[bool, dict, float, int, list, str, tuple, None]
"""Typing for the various types that a Lambda can be invoked with"""

LambdaSqsRecords = list[
    dict[
        str,
        Union[
            str,
            dict[str, str],
            dict[
                str,
                dict[str, dict[str, Union[str, bytes, list[str], list[bytes]]]],
            ],
        ],
    ]
]


@dataclass(frozen=True, init=False)
class Message:
    """
    Message dataclass to manage message attributes and properties
    """

    body: str
    """The body"""
    group_id: str
    """The SQS group id"""
    length: int
    """The length, as SQS calculates it"""
    message_attributes: dict[str, MessageAttributeValueTypeDef]
    """The user-defined attributes"""
    message_type: MessageType
    """The EchoStream message type"""
    tracking_id: str
    """The tracking id"""
    previous_tracking_ids: list[str]
    """A list of previous tracking ids. Populated if the original message was split"""

    def __init__(
        self,
        body: str,
        message_type: MessageType,
        group_id: str = None,
        previous_tracking_ids: Union[list[str], str] = None,
        tracking_id: str = None,
    ) -> None:
        super().__init__()
        super().__setattr__("body", body)
        super().__setattr__("group_id", group_id)
        super().__setattr__("message_type", message_type)
        super().__setattr__("tracking_id", tracking_id or uuid4().hex)
        if isinstance(previous_tracking_ids, str):
            previous_tracking_ids = json.loads(previous_tracking_ids)
        super().__setattr__(
            "previous_tracking_ids",
            previous_tracking_ids if previous_tracking_ids else None,
        )
        message_attributes = dict(
            trackingId=MessageAttributeValueTypeDef(
                DataType="String", StringValue=self.tracking_id
            )
        )
        if self.previous_tracking_ids:
            message_attributes["prevTrackingIds"] = MessageAttributeValueTypeDef(
                DataType="String",
                StringValue=json.dumps(
                    self.previous_tracking_ids, separators=(",", ":")
                ),
            )
        super().__setattr__("message_attributes", message_attributes)
        length = len(self.body)
        for name, attribute in self.message_attributes.items():
            value = attribute[
                "StringValue"
                if (data_type := attribute["DataType"]) in ("String", "Number")
                else "BinaryValue"
            ]
            length += len(name) + len(data_type) + len(value)
        if length > 262144:
            raise ValueError(f"Message is > 262,144 in size")
        super().__setattr__("length", length)

    def __len__(self) -> int:
        return self.length

    def _sqs_message(self, node: Node) -> dict:
        return dict(
            MessageAttributes=self.message_attributes,
            MessageBody=self.body,
            MessageGroupId=self.group_id or node.name.replace(" ", "_"),
        )


@dataclass(frozen=True)
class MessageType:
    """
    Dataclass for messagetype
    """

    auditor: Auditor
    """The auditor"""
    name: str
    """The name"""


class Node(ABC):
    """
    Base level node class. Used by threading and asyncio modules to interact with echostream nodes.
    """

    def __init__(
        self,
        *,
        appsync_endpoint: str = None,
        bulk_data_acceleration: bool = False,
        client_id: str = None,
        gql_transport_cls: type = CognitoRequestsHTTPTransport,
        name: str = None,
        password: str = None,
        tenant: str = None,
        timeout: float = None,
        user_pool_id: str = None,
        username: str = None,
    ) -> None:
        super().__init__()
        self.__cognito = Cognito(
            client_id=client_id or environ["CLIENT_ID"],
            user_pool_id=user_pool_id or environ["USER_POOL_ID"],
            username=username or environ["USER_NAME"],
        )
        self.__cognito.authenticate(password=password or environ["PASSWORD"])
        name = name or environ["NODE"]
        tenant = tenant or environ["TENANT"]
        gql_client = GqlClient(
            fetch_schema_from_transport=True,
            transport=CognitoRequestsHTTPTransport(
                self.__cognito,
                appsync_endpoint or environ["APPSYNC_ENDPOINT"],
            ),
        )
        with gql_client as session:
            data: dict[str, Union[str, dict]] = session.execute(
                _GET_APP_GQL,
                variable_values=dict(name=name, tenant=tenant),
            )["GetNode"]
        self.__app = data["app"]["name"]
        self.__app_type = data["app"]["__typename"]
        self.__audit_records_endpoint = data["app"]["auditRecordsEndpoint"]
        self.__bulk_data_acceleration = bulk_data_acceleration
        self.__config: dict[str, Any] = None
        self.__gql_client = GqlClient(
            fetch_schema_from_transport=True,
            transport=gql_transport_cls(
                self.__cognito,
                appsync_endpoint or environ["APPSYNC_ENDPOINT"],
            ),
        )
        self.__name = name
        self.__node_type = data["__typename"]
        self.__session = Session(
            botocore_session=_NodeBotocoreSession(node=self, gql_client=gql_client),
            region_name=data["tenant"]["region"],
        )
        self.__sources: frozenset[Edge] = None
        self.__sqs_client: SQSClient = (
            Session(region_name=data["tenant"]["region"])
            if self.__app_type == "CrossAccountApp"
            else self.__session
        ).client(
            "sqs",
            config=Config(
                max_pool_connections=min(20, ((cpu_count() or 1) + 4) * 2),
                retries={"mode": "standard"},
            ),
        )
        self.__table: str = (
            data["tenant"]["table"] if data["app"].get("tableAccess") else None
        )
        self.__targets: frozenset[Edge] = None
        self.__tenant = tenant
        self.__timeout = timeout or 0.1
        self._receive_message_type: MessageType = None
        self._send_message_type: MessageType = None

    @property
    def _audit_records_endpoint(self) -> str:
        return self.__audit_records_endpoint

    @property
    def _cognito(self) -> Cognito:
        return self.__cognito

    @property
    def _gql_client(self) -> GqlClient:
        return self.__gql_client

    @property
    def _sources(self) -> frozenset[Edge]:
        return self.__sources

    @_sources.setter
    def _sources(self, sources: set[Edge]) -> None:
        self.__sources = frozenset(sources)

    @property
    def _sqs_client(self) -> SQSClient:
        return self.__sqs_client

    @property
    def _targets(self) -> frozenset[Edge]:
        return self.__targets

    @_targets.setter
    def _targets(self, targets: set[Edge]) -> None:
        self.__targets = frozenset(targets)

    @property
    def app(self) -> str:
        return self.__app

    @property
    def app_type(self) -> str:
        return self.__app_type

    @property
    def bulk_data_acceleration(self) -> bool:
        return self.__bulk_data_acceleration

    @property
    def config(self) -> dict[str, Any]:
        return self.__config

    @config.setter
    def config(self, config: dict[str, Any]) -> None:
        self.__config = config

    def create_message(
        self,
        /,
        body: str,
        *,
        group_id: str = None,
        previous_tracking_ids: Union[list[str], str] = None,
        tracking_id: str = None,
    ) -> Message:
        """
        Creates message as per the message standard of echostream.

        Arguments:
        body - [POSITIONAL ARGUMENT] content of the message
        group_id - [KEYWORD ARGUMENT] group id
        previous_tracking_ids - [KEYWORD ARGUMENT] previous tracking id of the message if available
        tracking_id - [KEYWORD ARGUMENT] tracking id of the message if available
        """
        return Message(
            body=body,
            group_id=group_id,
            message_type=self.send_message_type,
            previous_tracking_ids=previous_tracking_ids,
            tracking_id=tracking_id,
        )

    @property
    def name(self) -> str:
        return self.__name

    @property
    def node_type(self) -> str:
        return self.__node_type

    @property
    def receive_message_type(self) -> MessageType:
        return self._receive_message_type

    @property
    def send_message_type(self) -> MessageType:
        return self._send_message_type

    @property
    def sources(self) -> frozenset[Edge]:
        return self._sources

    @property
    def table(self) -> Table:
        if self.__table:
            return self.__session.resource("dynamodb").Table(self.__table)
        raise RuntimeError(f"App {self.app} does not have tableAccess")

    @property
    def targets(self) -> frozenset[Edge]:
        return self._targets

    @property
    def tenant(self) -> str:
        return self.__tenant

    @property
    def timeout(self) -> float:
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        self.__timeout = timeout or 0.1


@dataclass(frozen=True)
class PresignedPost:
    """
    PresignedPost objects are part of the Bulk Data Storage system
    and are used to POST bulk data.
    """

    fields: dict[str, str]
    """The fields required to be sent when POSTing bulk data"""
    url: str
    """The POST url used to POST bulk data"""


@dataclass(frozen=True)
class PresignedPut:
    """
    PresignedPut objects are part of the Bulk Data Storage system
    and are used to PUT bulk data.
    """

    headers: dict[str, str]
    """The headers required to be sent when PUTing bulk data"""
    url: str
    """The PUT url used to PUT bulk data"""
