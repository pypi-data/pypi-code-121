import grpc


class ModelaException(Exception):
    """
    Error handling for gRPC and application-level errors is done with exceptions. ModelaException provides a base class
    for all exceptions raised by the Modela SDK.
    """

    def __init__(self, code: int, error: str, details: str, debug_string: str):
        super().__init__()
        self._code = code
        self._error = error
        self._details = details
        self._debug_string = debug_string

    @property
    def code(self):
        """
        The error code returned by the gRPC interface
        """
        return self._code

    @property
    def error(self):
        """
        The error code name returned by the gRPC interface
        """
        return self._error

    @property
    def details(self):
        """
        The error details returned by the Modela API gateway
        """
        return self._details

    @property
    def debug_string(self):
        """
        The error debug string returned by gRPC
        """
        return self._debug_string

    @staticmethod
    def process_error(err: grpc.RpcError):
        if err.code() == grpc.StatusCode.ALREADY_EXISTS.value:
            raise ResourceExistsException(err.code().value, err.code().name, err.details(), err.debug_error_string())
        if err.code() == grpc.StatusCode.NOT_FOUND:
            raise ResourceNotFoundException(err.code().value, err.code().name, err.details(), err.debug_error_string())
        elif err.code() == grpc.StatusCode.UNAUTHENTICATED:
            raise UnauthenticatedException(err.code().value, err.code().name, err.details(), err.debug_error_string())
        elif err.code() == grpc.StatusCode.PERMISSION_DENIED:
            raise PermissionDeniedException(err.code().value, err.code().name, err.details(), err.debug_error_string())
        elif err.code() == grpc.StatusCode.FAILED_PRECONDITION:
            raise InvalidResourceException(err.code().value, err.code().name, err.details(), err.debug_error_string())
        else:
            raise GrpcErrorException(err.code().value, err.code().name, err.details(), err.debug_error_string())

    def __str__(self):
        return "{details} ({error}, {code})".format(details=self.details, error=self.error, code=self.code)


class ResourceNotFoundException(ModelaException):
    """
    Exception raised in the case of a resource not being found in a namespace with a given name.
    """


class ResourceExistsException(ModelaException):
    """
    Exception raised in the case of a resource being created when it already exists.
    """


class UnauthenticatedException(ModelaException):
    """
    Exception raised in the case of the user being unauthenticated.
    """


class PermissionDeniedException(ModelaException):
    """
    Exception raised in the case of unauthorized access to a certain type of resource action.
    """


class InvalidResourceException(ModelaException):
    """
    Exception raised in the case of the application recognizing a resource update or create request to be invalid.
    """


class GrpcErrorException(ModelaException):
    """
    Exception raised in the case of any miscellaneous gRPC error
    """

