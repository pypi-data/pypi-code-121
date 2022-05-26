from sila2.framework.errors.framework_error import FrameworkError, FrameworkErrorType


class InvalidMetadata(FrameworkError):
    """
    Issued by a SiLA Server if a SiLA Client did not send the required SiLA Client Metadata,
    or when the received Metadata was invalid

    Notes
    -----
    This error is raised automatically by the SDK
    """

    def __init__(self, message: str):
        super().__init__(FrameworkErrorType.INVALID_METADATA, message)
