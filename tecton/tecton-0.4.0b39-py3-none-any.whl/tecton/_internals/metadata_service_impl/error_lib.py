import enum
import logging

from tecton._internals import errors
from tecton._internals.metadata_service_impl import auth_lib
from tecton._internals.metadata_service_impl import trace
from tecton._internals.tecton_errors import FailedPreconditionError
from tecton._internals.tecton_errors import TectonAPIInaccessibleError
from tecton._internals.tecton_errors import TectonAPIValidationError
from tecton_spark.logger import get_logging_level


class gRPCStatus(enum.Enum):
    """gRPC response status codes.

    Status codes are replicated here to avoid importing the `grpc.StatusCode` enum class,
    which requires the grpcio library.

    https://grpc.github.io/grpc/core/md_doc_statuscodes.html
    """

    OK = 0
    CANCELLED = 1
    UNKNOWN = 2
    INVALID_ARGUMENT = 3
    DEADLINE_EXCEEDED = 4
    NOT_FOUND = 5
    ALREADY_EXISTS = 6
    PERMISSION_DENIED = 7
    RESOURCE_EXHAUSTED = 8
    FAILED_PRECONDITION = 9
    ABORTED = 10
    OUT_OF_RANGE = 11
    UNIMPLEMENTED = 12
    INTERNAL = 13
    UNAVAILABLE = 14
    DATA_LOSS = 15
    UNAUTHENTICATED = 16


def raise_for_grpc_status(status_code: int, details: str, host_url: str):
    """
    Raise an exception based on a gRPC error status code.
    """
    if status_code == gRPCStatus.OK.value:
        return

    # Error handling
    if status_code == gRPCStatus.UNAVAILABLE.value:
        raise TectonAPIInaccessibleError(details, host_url)

    if status_code == gRPCStatus.INVALID_ARGUMENT.value:
        raise TectonAPIValidationError(details)

    if status_code == gRPCStatus.FAILED_PRECONDITION.value:
        raise FailedPreconditionError(details)

    if status_code == gRPCStatus.UNAUTHENTICATED.value:
        raise PermissionError(
            "Tecton credentials are not configured, have expired or are not valid. "
            + f"Run `tecton login` to authenticate. ({details})"
        )

    if status_code == gRPCStatus.PERMISSION_DENIED.value:
        if not auth_lib.request_has_token():
            # Remove this case in https://tecton.atlassian.net/browse/TEC-9107
            raise PermissionError(
                "Tecton credentials are not configured or have expired. Run `tecton login` to authenticate."
            )
        elif details != None and "InvalidToken" in details:
            # Remove this case in https://tecton.atlassian.net/browse/TEC-9107
            raise PermissionError(f"Configured Tecton credentials are not valid ({details}).")
        else:
            raise PermissionError(f"Insufficient permissions ({details}).")

    if get_logging_level() < logging.INFO:
        raise Exception(f"Unknown MDS exception. code={status_code}, details={details}")

    raise errors.INTERNAL_ERROR_FROM_MDS(details, trace.get_trace_id())
