import sys
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

MaxResults = int
NextToken = str
PageSize = int
Qos = int
Retain = bool
ShadowName = str
ThingName = str
Topic = str
errorMessage = str


class ConflictException(ServiceException):
    """The specified version does not match the version of the document."""

    message: Optional[errorMessage]


class InternalFailureException(ServiceException):
    """An unexpected error has occurred."""

    message: Optional[errorMessage]


class InvalidRequestException(ServiceException):
    """The request is not valid."""

    message: Optional[errorMessage]


class MethodNotAllowedException(ServiceException):
    """The specified combination of HTTP verb and URI is not supported."""

    message: Optional[errorMessage]


class RequestEntityTooLargeException(ServiceException):
    """The payload exceeds the maximum size allowed."""

    message: Optional[errorMessage]


class ResourceNotFoundException(ServiceException):
    """The specified resource does not exist."""

    message: Optional[errorMessage]


class ServiceUnavailableException(ServiceException):
    """The service is temporarily unavailable."""

    message: Optional[errorMessage]


class ThrottlingException(ServiceException):
    """The rate exceeds the limit."""

    message: Optional[errorMessage]


class UnauthorizedException(ServiceException):
    """You are not authorized to perform this operation."""

    message: Optional[errorMessage]


class UnsupportedDocumentEncodingException(ServiceException):
    """The document encoding is not supported."""

    message: Optional[errorMessage]


class DeleteThingShadowRequest(ServiceRequest):
    """The input for the DeleteThingShadow operation."""

    thingName: ThingName
    shadowName: Optional[ShadowName]


JsonDocument = bytes


class DeleteThingShadowResponse(TypedDict, total=False):
    """The output from the DeleteThingShadow operation."""

    payload: JsonDocument


class GetRetainedMessageRequest(ServiceRequest):
    """The input for the GetRetainedMessage operation."""

    topic: Topic


Timestamp = int
Payload = bytes


class GetRetainedMessageResponse(TypedDict, total=False):
    """The output from the GetRetainedMessage operation."""

    topic: Optional[Topic]
    payload: Optional[Payload]
    qos: Optional[Qos]
    lastModifiedTime: Optional[Timestamp]


class GetThingShadowRequest(ServiceRequest):
    """The input for the GetThingShadow operation."""

    thingName: ThingName
    shadowName: Optional[ShadowName]


class GetThingShadowResponse(TypedDict, total=False):
    """The output from the GetThingShadow operation."""

    payload: Optional[JsonDocument]


class ListNamedShadowsForThingRequest(ServiceRequest):
    thingName: ThingName
    nextToken: Optional[NextToken]
    pageSize: Optional[PageSize]


NamedShadowList = List[ShadowName]


class ListNamedShadowsForThingResponse(TypedDict, total=False):
    results: Optional[NamedShadowList]
    nextToken: Optional[NextToken]
    timestamp: Optional[Timestamp]


class ListRetainedMessagesRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


PayloadSize = int


class RetainedMessageSummary(TypedDict, total=False):
    """Information about a single retained message."""

    topic: Optional[Topic]
    payloadSize: Optional[PayloadSize]
    qos: Optional[Qos]
    lastModifiedTime: Optional[Timestamp]


RetainedMessageList = List[RetainedMessageSummary]


class ListRetainedMessagesResponse(TypedDict, total=False):
    retainedTopics: Optional[RetainedMessageList]
    nextToken: Optional[NextToken]


class PublishRequest(ServiceRequest):
    """The input for the Publish operation."""

    topic: Topic
    qos: Optional[Qos]
    retain: Optional[Retain]
    payload: Optional[Payload]


class UpdateThingShadowRequest(ServiceRequest):
    """The input for the UpdateThingShadow operation."""

    thingName: ThingName
    shadowName: Optional[ShadowName]
    payload: JsonDocument


class UpdateThingShadowResponse(TypedDict, total=False):
    """The output from the UpdateThingShadow operation."""

    payload: Optional[JsonDocument]


class IotDataApi:

    service = "iot-data"
    version = "2015-05-28"

    @handler("DeleteThingShadow")
    def delete_thing_shadow(
        self, context: RequestContext, thing_name: ThingName, shadow_name: ShadowName = None
    ) -> DeleteThingShadowResponse:
        """Deletes the shadow for the specified thing.

        Requires permission to access the
        `DeleteThingShadow <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        For more information, see
        `DeleteThingShadow <http://docs.aws.amazon.com/iot/latest/developerguide/API_DeleteThingShadow.html>`__
        in the IoT Developer Guide.

        :param thing_name: The name of the thing.
        :param shadow_name: The name of the shadow.
        :returns: DeleteThingShadowResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises MethodNotAllowedException:
        :raises UnsupportedDocumentEncodingException:
        """
        raise NotImplementedError

    @handler("GetRetainedMessage")
    def get_retained_message(
        self, context: RequestContext, topic: Topic
    ) -> GetRetainedMessageResponse:
        """Gets the details of a single retained message for the specified topic.

        This action returns the message payload of the retained message, which
        can incur messaging costs. To list only the topic names of the retained
        messages, call
        `ListRetainedMessages </iot/latest/developerguide/API_iotdata_ListRetainedMessages.html>`__.

        Requires permission to access the
        `GetRetainedMessage <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotfleethubfordevicemanagement.html#awsiotfleethubfordevicemanagement-actions-as-permissions>`__
        action.

        For more information about messaging costs, see `Amazon Web Services IoT
        Core pricing -
        Messaging <http://aws.amazon.com/iot-core/pricing/#Messaging>`__.

        :param topic: The topic name of the retained message to retrieve.
        :returns: GetRetainedMessageResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises MethodNotAllowedException:
        """
        raise NotImplementedError

    @handler("GetThingShadow")
    def get_thing_shadow(
        self, context: RequestContext, thing_name: ThingName, shadow_name: ShadowName = None
    ) -> GetThingShadowResponse:
        """Gets the shadow for the specified thing.

        Requires permission to access the
        `GetThingShadow <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        For more information, see
        `GetThingShadow <http://docs.aws.amazon.com/iot/latest/developerguide/API_GetThingShadow.html>`__
        in the IoT Developer Guide.

        :param thing_name: The name of the thing.
        :param shadow_name: The name of the shadow.
        :returns: GetThingShadowResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises MethodNotAllowedException:
        :raises UnsupportedDocumentEncodingException:
        """
        raise NotImplementedError

    @handler("ListNamedShadowsForThing")
    def list_named_shadows_for_thing(
        self,
        context: RequestContext,
        thing_name: ThingName,
        next_token: NextToken = None,
        page_size: PageSize = None,
    ) -> ListNamedShadowsForThingResponse:
        """Lists the shadows for the specified thing.

        Requires permission to access the
        `ListNamedShadowsForThing <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The name of the thing.
        :param next_token: The token to retrieve the next set of results.
        :param page_size: The result page size.
        :returns: ListNamedShadowsForThingResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises MethodNotAllowedException:
        """
        raise NotImplementedError

    @handler("ListRetainedMessages")
    def list_retained_messages(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListRetainedMessagesResponse:
        """Lists summary information about the retained messages stored for the
        account.

        This action returns only the topic names of the retained messages. It
        doesn't return any message payloads. Although this action doesn't return
        a message payload, it can still incur messaging costs.

        To get the message payload of a retained message, call
        `GetRetainedMessage <https://docs.aws.amazon.com/iot/latest/developerguide/API_iotdata_GetRetainedMessage.html>`__
        with the topic name of the retained message.

        Requires permission to access the
        `ListRetainedMessages <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotfleethubfordevicemanagement.html#awsiotfleethubfordevicemanagement-actions-as-permissions>`__
        action.

        For more information about messaging costs, see `Amazon Web Services IoT
        Core pricing -
        Messaging <http://aws.amazon.com/iot-core/pricing/#Messaging>`__.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListRetainedMessagesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises MethodNotAllowedException:
        """
        raise NotImplementedError

    @handler("Publish")
    def publish(
        self,
        context: RequestContext,
        topic: Topic,
        qos: Qos = None,
        retain: Retain = None,
        payload: Payload = None,
    ) -> None:
        """Publishes an MQTT message.

        Requires permission to access the
        `Publish <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        For more information about MQTT messages, see `MQTT
        Protocol <http://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html>`__
        in the IoT Developer Guide.

        For more information about messaging costs, see `Amazon Web Services IoT
        Core pricing -
        Messaging <http://aws.amazon.com/iot-core/pricing/#Messaging>`__.

        :param topic: The name of the MQTT topic.
        :param qos: The Quality of Service (QoS) level.
        :param retain: A Boolean value that determines whether to set the RETAIN flag when the
        message is published.
        :param payload: The message body.
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises UnauthorizedException:
        :raises MethodNotAllowedException:
        """
        raise NotImplementedError

    @handler("UpdateThingShadow")
    def update_thing_shadow(
        self,
        context: RequestContext,
        thing_name: ThingName,
        payload: JsonDocument,
        shadow_name: ShadowName = None,
    ) -> UpdateThingShadowResponse:
        """Updates the shadow for the specified thing.

        Requires permission to access the
        `UpdateThingShadow <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        For more information, see
        `UpdateThingShadow <http://docs.aws.amazon.com/iot/latest/developerguide/API_UpdateThingShadow.html>`__
        in the IoT Developer Guide.

        :param thing_name: The name of the thing.
        :param payload: The state information, in JSON format.
        :param shadow_name: The name of the shadow.
        :returns: UpdateThingShadowResponse
        :raises ConflictException:
        :raises RequestEntityTooLargeException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises MethodNotAllowedException:
        :raises UnsupportedDocumentEncodingException:
        """
        raise NotImplementedError
