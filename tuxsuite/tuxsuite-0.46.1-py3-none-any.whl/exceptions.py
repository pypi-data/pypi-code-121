# -*- coding: utf-8 -*-


class TuxSuiteError(Exception):
    """Base class for all TuxSuite exceptions"""

    error_help = ""
    error_type = ""


class CantGetConfiguration(TuxSuiteError):
    error_help = "Problem reading configuration"
    error_type = "configuration"


class InvalidConfiguration(TuxSuiteError):
    error_help = "Invalid configuration"
    error_type = "configuration"


class TokenNotFound(TuxSuiteError):
    error_help = "No token provided"
    error_type = "Configuration"


class URLNotFound(TuxSuiteError):
    error_help = "A tuxsuite URL cannot be found"
    error_type = "Configuration"


class BadRequest(TuxSuiteError):
    error_help = "A tuxsuite API call failed"
    error_type = "API"


class InvalidToken(TuxSuiteError):
    error_help = "The provided token was not accepted by the server"
    error_type = "API"


class Timeout(TuxSuiteError):
    error_help = "A tuxsuite API call failed"
    error_type = "API"


class UnsupportedJob(TuxSuiteError):
    error_help = "Unsupported Job Type"
    error_type = "configuration"
