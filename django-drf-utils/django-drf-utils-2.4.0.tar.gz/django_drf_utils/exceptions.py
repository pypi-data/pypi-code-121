from rest_framework import status
from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable, please try again later."
    default_code = "service_unavailable"


class Unimplemented(APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = "Service not available."
    default_code = "not_implemented"


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Request conflict with current state of the target resource."
    default_code = "conflict"


class UnprocessableEntityError(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Target resource could NOT be updated with request body."
    default_code = "unprocessable_entity"
