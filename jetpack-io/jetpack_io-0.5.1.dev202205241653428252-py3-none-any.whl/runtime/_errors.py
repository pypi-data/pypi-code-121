class JetpackError(Exception):
    """Base class for exceptions in this module"""

    pass


class SystemError(JetpackError):
    """Exception raised for errors in the Jetpack runtime and kubernetes."""

    def __init__(self, message: str) -> None:
        self.message = message


class ApplicationError(JetpackError):
    """Exception raised for errors from application-code that is using the SDK.

    TODO DEV-157
    For exceptions raised by remote functions and jobs, we serialize the
    userland exception in the backend and save it here. The userland exception
    is re-raised by the SDK for the caller of the remote function or job.
    """

    def __init__(self, message: str) -> None:
        self.message = message
