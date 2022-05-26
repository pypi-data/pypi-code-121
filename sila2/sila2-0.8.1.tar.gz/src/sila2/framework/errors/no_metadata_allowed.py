from sila2.framework.errors.framework_error import FrameworkError, FrameworkErrorType


class NoMetadataAllowed(FrameworkError):
    """
    Issued by a SiLA Server when receiving a request to the SiLA Service Feature that contains SiLA Client Metadata

    Notes
    -----
    This error is raised automatically by the SDK
    """

    def __init__(self, message: str):
        super().__init__(FrameworkErrorType.NO_METADATA_ALLOWED, message)
