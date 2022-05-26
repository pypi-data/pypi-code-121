from sila2.framework.errors.framework_error import FrameworkError, FrameworkErrorType


class CommandExecutionNotAccepted(FrameworkError):
    """
    Issued when a SiLA Server does not allow the requested command execution

    Notes
    -----
    This is NOT done automatically by the SDK
    """

    def __init__(self, message: str):
        super().__init__(FrameworkErrorType.COMMAND_EXECUTION_NOT_ACCEPTED, message)
