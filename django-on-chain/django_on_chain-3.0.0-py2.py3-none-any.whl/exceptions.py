from django.utils.translation import ugettext_lazy as _
from rest_framework import status


class ServiceError(Exception):
    """
    Base class for microservice errors

    Typically a Http response is generated from this.
    """
    def __init__(self, type, message, errors=None, suggested_http_status=None):
        super(ServiceError, self).__init__(message)
        self.type = type
        self.message = message
        self.errors = errors
        self.suggested_http_status = suggested_http_status


class BadRequestError(ServiceError):
    """
    Is raised when an invalid request comes from client
    """
    def __init__(self, type, message, errors=None, suggested_http_status=None):
        super(BadRequestError, self).__init__(type, message, errors,
                                              suggested_http_status or status.HTTP_400_BAD_REQUEST)


class NotFoundError(ServiceError):
    """
    Is raised when a requested entity does not exist
    """
    def __init__(self,
                 type='not_found',
                 message=_('Resource was not found'),
                 errors=None):
        super(NotFoundError, self).__init__(type, message, errors, status.HTTP_404_NOT_FOUND)


class UnauthorizedError(ServiceError):
    """
    Is raised when a request has not valid authentication credentials
    """
    def __init__(self,
                 type='unauthorized',
                 message=_('Request is not authorized'),
                 errors=None):
        super(UnauthorizedError, self).__init__(type, message, errors, status.HTTP_401_UNAUTHORIZED)


class AccessForbiddenError(ServiceError):
    """
    Is raised when the user is logged in, but has not permission to perform the request
    """
    def __init__(self,
                 type='access_forbidden',
                 message=_('You do not have permission to perform this action.'),
                 errors=None):
        super(AccessForbiddenError, self).__init__(type, message, errors, status.HTTP_403_FORBIDDEN)


class ServerError(ServiceError):
    """
    Is raised when an internal server error occurs
    """
    def __init__(self,
                 type='server_error',
                 message=_('Unknown error; please try again later'),
                 errors=None,
                 suggested_http_status=None):
        super(ServerError, self).__init__(type, message, errors,
                                          suggested_http_status or status.HTTP_500_INTERNAL_SERVER_ERROR)
