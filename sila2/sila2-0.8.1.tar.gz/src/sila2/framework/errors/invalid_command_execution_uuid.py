from sila2.framework.errors.framework_error import FrameworkError, FrameworkErrorType


class InvalidCommandExecutionUUID(FrameworkError):
    """
    Issued by a SiLA Server when a SiLA Client is trying to get or subscribe to command execution information,
    intermediate responses or responses of an observable command with an invalid command execution UUID

    Notes
    -----
    This error is raised automatically by the SDK
    """

    def __init__(self, message: str):
        super().__init__(FrameworkErrorType.INVALID_COMMAND_EXECUTION_UUID, message)
