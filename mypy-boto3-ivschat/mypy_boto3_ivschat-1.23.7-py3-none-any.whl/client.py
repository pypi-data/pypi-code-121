"""
Type annotations for ivschat service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_ivschat.client import ivschatClient

    session = Session()
    client: ivschatClient = session.client("ivschat")
    ```
"""
from typing import Any, Dict, Mapping, Sequence, Type

from botocore.client import BaseClient, ClientMeta

from .literals import ChatTokenCapabilityType
from .type_defs import (
    CreateChatTokenResponseTypeDef,
    CreateRoomResponseTypeDef,
    DeleteMessageResponseTypeDef,
    GetRoomResponseTypeDef,
    ListRoomsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    MessageReviewHandlerTypeDef,
    SendEventResponseTypeDef,
    UpdateRoomResponseTypeDef,
)

__all__ = ("ivschatClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    PendingVerification: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class ivschatClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        ivschatClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#can_paginate)
        """

    def create_chat_token(
        self,
        *,
        roomIdentifier: str,
        userId: str,
        attributes: Mapping[str, str] = ...,
        capabilities: Sequence[ChatTokenCapabilityType] = ...,
        sessionDurationInMinutes: int = ...
    ) -> CreateChatTokenResponseTypeDef:
        """
        Creates an encrypted token that is used to establish an individual WebSocket
        connection to a room.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.create_chat_token)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#create_chat_token)
        """

    def create_room(
        self,
        *,
        maximumMessageLength: int = ...,
        maximumMessageRatePerSecond: int = ...,
        messageReviewHandler: MessageReviewHandlerTypeDef = ...,
        name: str = ...,
        tags: Mapping[str, str] = ...
    ) -> CreateRoomResponseTypeDef:
        """
        Creates a room that allows clients to connect and pass messages.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.create_room)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#create_room)
        """

    def delete_message(
        self, *, id: str, roomIdentifier: str, reason: str = ...
    ) -> DeleteMessageResponseTypeDef:
        """
        Sends an event to a specific room which directs clients to delete a specific
        message; that is, unrender it from view and delete it from the client’s chat
        history.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.delete_message)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#delete_message)
        """

    def delete_room(self, *, identifier: str) -> None:
        """
        Deletes the specified room.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.delete_room)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#delete_room)
        """

    def disconnect_user(
        self, *, roomIdentifier: str, userId: str, reason: str = ...
    ) -> Dict[str, Any]:
        """
        Disconnects all connections using a specified user ID from a room.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.disconnect_user)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#disconnect_user)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#generate_presigned_url)
        """

    def get_room(self, *, identifier: str) -> GetRoomResponseTypeDef:
        """
        Gets the specified room.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.get_room)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#get_room)
        """

    def list_rooms(
        self,
        *,
        maxResults: int = ...,
        messageReviewHandlerUri: str = ...,
        name: str = ...,
        nextToken: str = ...
    ) -> ListRoomsResponseTypeDef:
        """
        Gets summary information about all your rooms in the AWS region where the API
        request is processed.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.list_rooms)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#list_rooms)
        """

    def list_tags_for_resource(self, *, resourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Gets information about AWS tags for the specified ARN.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#list_tags_for_resource)
        """

    def send_event(
        self, *, eventName: str, roomIdentifier: str, attributes: Mapping[str, str] = ...
    ) -> SendEventResponseTypeDef:
        """
        Sends an event to a room.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.send_event)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#send_event)
        """

    def tag_resource(self, *, resourceArn: str, tags: Mapping[str, str]) -> Dict[str, Any]:
        """
        Adds or updates tags for the AWS resource with the specified ARN.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#tag_resource)
        """

    def untag_resource(self, *, resourceArn: str, tagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes tags from the resource with the specified ARN.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#untag_resource)
        """

    def update_room(
        self,
        *,
        identifier: str,
        maximumMessageLength: int = ...,
        maximumMessageRatePerSecond: int = ...,
        messageReviewHandler: MessageReviewHandlerTypeDef = ...,
        name: str = ...
    ) -> UpdateRoomResponseTypeDef:
        """
        Updates a room’s configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ivschat.html#ivschat.Client.update_room)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/client/#update_room)
        """
