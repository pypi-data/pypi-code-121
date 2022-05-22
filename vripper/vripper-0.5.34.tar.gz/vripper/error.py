class UnsupportedHostError(Exception):
    """Raised when the host is unsupported (yet)"""
    pass


class DeprecatedHostError(Exception):
    """Raised when the host is unsupported (permanently)"""
    pass


class InsufficientFileCountError(Exception):
    """Raised when the final file count in a post does not meet the required value"""
    pass


class ImagePermanentlyUnavailableError(Exception):
    """Raised when the image was permanently deleted"""
    pass


class NoNativeParserError(Exception):
    """
    Raised when the underlying URL for an image cannot be determined by the native parser.
    This exception acts as the signal to use the secondary parser (ie. 3rd party).
    """
    pass
