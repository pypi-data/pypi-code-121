class DataSDKError(Exception):
    """Base exception class."""


class DataFrameParsingError(DataSDKError):
    """Unable to parse DataFrame"""


class UnknownMediaTypeError(DataSDKError):
    """Unknown Media Type"""


class UnknownDatasetNameError(DataSDKError):
    """Unknown Dataset Name"""


class AuthenticationError(DataSDKError):
    """AuthenticationError"""
