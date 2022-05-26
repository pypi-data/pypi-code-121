from __future__ import annotations

import grpc
from grpc import RpcError


class SilaConnectionError(Exception):
    """
    Any error during SiLA communication that is not actively issued by the SiLA Server or SiLA Client

    Notes
    -----
    This error is raised by the :py:class:`sila2.client.SilaClient` class when a non-SiLA error is raised
    """

    exception: Exception
    """The exception that caused this error"""

    @classmethod
    def from_exception(cls, exception: Exception) -> SilaConnectionError:
        if isinstance(exception, RpcError):
            if exception.code() == grpc.StatusCode.UNAVAILABLE:
                message = "Failed to establish connection to the server"
            else:
                message = f"{exception.code().name} - {exception.details()}"
            message = f"{exception.code().name} - {message}"
        else:
            message = str(exception)
        err = cls(message)
        err.exception = exception
        return err
