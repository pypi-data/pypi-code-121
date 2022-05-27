import sys
from datetime import datetime
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

_string = str


class ForbiddenException(ServiceException):
    """The caller is not authorized to invoke this operation."""


class GoneException(ServiceException):
    """The connection with the provided id no longer exists."""


class PayloadTooLargeException(ServiceException):
    """The data has exceeded the maximum size allowed."""

    Message: Optional[_string]


class LimitExceededException(ServiceException):
    """The client is sending more than the allowed number of requests per unit
    of time or the WebSocket client side buffer is full.
    """


Data = bytes


class DeleteConnectionRequest(ServiceRequest):
    ConnectionId: _string


class GetConnectionRequest(ServiceRequest):
    ConnectionId: _string


_timestampIso8601 = datetime


class Identity(TypedDict, total=False):
    SourceIp: _string
    UserAgent: _string


class GetConnectionResponse(TypedDict, total=False):
    ConnectedAt: Optional[_timestampIso8601]
    Identity: Optional[Identity]
    LastActiveAt: Optional[_timestampIso8601]


class PostToConnectionRequest(ServiceRequest):
    Data: Data
    ConnectionId: _string


class ApigatewaymanagementapiApi:

    service = "apigatewaymanagementapi"
    version = "2018-11-29"

    @handler("DeleteConnection")
    def delete_connection(self, context: RequestContext, connection_id: _string) -> None:
        """Delete the connection with the provided id.

        :param connection_id: .
        :raises GoneException:
        :raises LimitExceededException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("GetConnection")
    def get_connection(
        self, context: RequestContext, connection_id: _string
    ) -> GetConnectionResponse:
        """Get information about the connection with the provided id.

        :param connection_id: .
        :returns: GetConnectionResponse
        :raises GoneException:
        :raises LimitExceededException:
        :raises ForbiddenException:
        """
        raise NotImplementedError

    @handler("PostToConnection")
    def post_to_connection(
        self, context: RequestContext, connection_id: _string, data: Data
    ) -> None:
        """Sends the provided data to the specified connection.

        :param connection_id: The identifier of the connection that a specific client is using.
        :param data: The data to be sent to the client specified by its connection id.
        :raises GoneException:
        :raises LimitExceededException:
        :raises PayloadTooLargeException:
        :raises ForbiddenException:
        """
        raise NotImplementedError
