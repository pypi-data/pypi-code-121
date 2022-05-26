from sila2.framework.errors.framework_error import FrameworkError, FrameworkErrorType


class CommandExecutionNotFinished(FrameworkError):
    """
    Issued by a SiLA Server when a SiLA Client is trying to get the command response of an observable command
    when the command has not been finished yet

    Notes
    -----
    This error is raised automatically by the SDK
    """

    def __init__(self, message: str):
        super().__init__(FrameworkErrorType.COMMAND_EXECUTION_NOT_FINISHED, message)
