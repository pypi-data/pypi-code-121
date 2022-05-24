"""
Type annotations for ivschat service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ivschat/type_defs/)

Usage::

    ```python
    from mypy_boto3_ivschat.type_defs import CreateChatTokenRequestRequestTypeDef

    data: CreateChatTokenRequestRequestTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import ChatTokenCapabilityType, FallbackResultType

if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "CreateChatTokenRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "MessageReviewHandlerTypeDef",
    "DeleteMessageRequestRequestTypeDef",
    "DeleteRoomRequestRequestTypeDef",
    "DisconnectUserRequestRequestTypeDef",
    "GetRoomRequestRequestTypeDef",
    "ListRoomsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "SendEventRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "CreateChatTokenResponseTypeDef",
    "DeleteMessageResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "SendEventResponseTypeDef",
    "CreateRoomRequestRequestTypeDef",
    "CreateRoomResponseTypeDef",
    "GetRoomResponseTypeDef",
    "RoomSummaryTypeDef",
    "UpdateRoomRequestRequestTypeDef",
    "UpdateRoomResponseTypeDef",
    "ListRoomsResponseTypeDef",
)

_RequiredCreateChatTokenRequestRequestTypeDef = TypedDict(
    "_RequiredCreateChatTokenRequestRequestTypeDef",
    {
        "roomIdentifier": str,
        "userId": str,
    },
)
_OptionalCreateChatTokenRequestRequestTypeDef = TypedDict(
    "_OptionalCreateChatTokenRequestRequestTypeDef",
    {
        "attributes": Mapping[str, str],
        "capabilities": Sequence[ChatTokenCapabilityType],
        "sessionDurationInMinutes": int,
    },
    total=False,
)


class CreateChatTokenRequestRequestTypeDef(
    _RequiredCreateChatTokenRequestRequestTypeDef, _OptionalCreateChatTokenRequestRequestTypeDef
):
    pass


ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

MessageReviewHandlerTypeDef = TypedDict(
    "MessageReviewHandlerTypeDef",
    {
        "fallbackResult": FallbackResultType,
        "uri": str,
    },
    total=False,
)

_RequiredDeleteMessageRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteMessageRequestRequestTypeDef",
    {
        "id": str,
        "roomIdentifier": str,
    },
)
_OptionalDeleteMessageRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteMessageRequestRequestTypeDef",
    {
        "reason": str,
    },
    total=False,
)


class DeleteMessageRequestRequestTypeDef(
    _RequiredDeleteMessageRequestRequestTypeDef, _OptionalDeleteMessageRequestRequestTypeDef
):
    pass


DeleteRoomRequestRequestTypeDef = TypedDict(
    "DeleteRoomRequestRequestTypeDef",
    {
        "identifier": str,
    },
)

_RequiredDisconnectUserRequestRequestTypeDef = TypedDict(
    "_RequiredDisconnectUserRequestRequestTypeDef",
    {
        "roomIdentifier": str,
        "userId": str,
    },
)
_OptionalDisconnectUserRequestRequestTypeDef = TypedDict(
    "_OptionalDisconnectUserRequestRequestTypeDef",
    {
        "reason": str,
    },
    total=False,
)


class DisconnectUserRequestRequestTypeDef(
    _RequiredDisconnectUserRequestRequestTypeDef, _OptionalDisconnectUserRequestRequestTypeDef
):
    pass


GetRoomRequestRequestTypeDef = TypedDict(
    "GetRoomRequestRequestTypeDef",
    {
        "identifier": str,
    },
)

ListRoomsRequestRequestTypeDef = TypedDict(
    "ListRoomsRequestRequestTypeDef",
    {
        "maxResults": int,
        "messageReviewHandlerUri": str,
        "name": str,
        "nextToken": str,
    },
    total=False,
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

_RequiredSendEventRequestRequestTypeDef = TypedDict(
    "_RequiredSendEventRequestRequestTypeDef",
    {
        "eventName": str,
        "roomIdentifier": str,
    },
)
_OptionalSendEventRequestRequestTypeDef = TypedDict(
    "_OptionalSendEventRequestRequestTypeDef",
    {
        "attributes": Mapping[str, str],
    },
    total=False,
)


class SendEventRequestRequestTypeDef(
    _RequiredSendEventRequestRequestTypeDef, _OptionalSendEventRequestRequestTypeDef
):
    pass


TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

CreateChatTokenResponseTypeDef = TypedDict(
    "CreateChatTokenResponseTypeDef",
    {
        "sessionExpirationTime": datetime,
        "token": str,
        "tokenExpirationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteMessageResponseTypeDef = TypedDict(
    "DeleteMessageResponseTypeDef",
    {
        "id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SendEventResponseTypeDef = TypedDict(
    "SendEventResponseTypeDef",
    {
        "id": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRoomRequestRequestTypeDef = TypedDict(
    "CreateRoomRequestRequestTypeDef",
    {
        "maximumMessageLength": int,
        "maximumMessageRatePerSecond": int,
        "messageReviewHandler": MessageReviewHandlerTypeDef,
        "name": str,
        "tags": Mapping[str, str],
    },
    total=False,
)

CreateRoomResponseTypeDef = TypedDict(
    "CreateRoomResponseTypeDef",
    {
        "arn": str,
        "createTime": datetime,
        "id": str,
        "maximumMessageLength": int,
        "maximumMessageRatePerSecond": int,
        "messageReviewHandler": MessageReviewHandlerTypeDef,
        "name": str,
        "tags": Dict[str, str],
        "updateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRoomResponseTypeDef = TypedDict(
    "GetRoomResponseTypeDef",
    {
        "arn": str,
        "createTime": datetime,
        "id": str,
        "maximumMessageLength": int,
        "maximumMessageRatePerSecond": int,
        "messageReviewHandler": MessageReviewHandlerTypeDef,
        "name": str,
        "tags": Dict[str, str],
        "updateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RoomSummaryTypeDef = TypedDict(
    "RoomSummaryTypeDef",
    {
        "arn": str,
        "createTime": datetime,
        "id": str,
        "messageReviewHandler": MessageReviewHandlerTypeDef,
        "name": str,
        "tags": Dict[str, str],
        "updateTime": datetime,
    },
    total=False,
)

_RequiredUpdateRoomRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateRoomRequestRequestTypeDef",
    {
        "identifier": str,
    },
)
_OptionalUpdateRoomRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateRoomRequestRequestTypeDef",
    {
        "maximumMessageLength": int,
        "maximumMessageRatePerSecond": int,
        "messageReviewHandler": MessageReviewHandlerTypeDef,
        "name": str,
    },
    total=False,
)


class UpdateRoomRequestRequestTypeDef(
    _RequiredUpdateRoomRequestRequestTypeDef, _OptionalUpdateRoomRequestRequestTypeDef
):
    pass


UpdateRoomResponseTypeDef = TypedDict(
    "UpdateRoomResponseTypeDef",
    {
        "arn": str,
        "createTime": datetime,
        "id": str,
        "maximumMessageLength": int,
        "maximumMessageRatePerSecond": int,
        "messageReviewHandler": MessageReviewHandlerTypeDef,
        "name": str,
        "tags": Dict[str, str],
        "updateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListRoomsResponseTypeDef = TypedDict(
    "ListRoomsResponseTypeDef",
    {
        "nextToken": str,
        "rooms": List[RoomSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
