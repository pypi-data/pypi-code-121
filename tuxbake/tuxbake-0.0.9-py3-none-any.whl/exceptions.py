class TuxbakeError(Exception):
    """Base class for all Tuxbuild exceptions"""

    error_help = ""
    error_type = ""


class TuxbakeRunCmdError(TuxbakeError):
    error_help = "Process call failed"
    error_type = "Configuration"


class TuxbakeParsingError(TuxbakeError):
    error_help = "Error while parsing API arguments"
    error_type = "Validation"


class TuxbakeValidationError(TuxbakeError):
    error_help = "Error while validating API arguments"
    error_type = "Validation"
