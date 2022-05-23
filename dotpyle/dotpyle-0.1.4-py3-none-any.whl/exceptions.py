"""Dotpyle exceptions definition"""

from dotpyle.utils import constants


class DotpyleException(Exception):
    """Dotpyle generic exception"""

    def __init__(self, message: str = "", code: int = 1):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ConfigHandlerException(DotpyleException):
    """ConfigHandler custom exception"""

    def __init__(self, message: str):
        message = "[CONFIG] " + message
        super().__init__(message, constants.CONFIG_HANDLER_ERROR_CODE)
