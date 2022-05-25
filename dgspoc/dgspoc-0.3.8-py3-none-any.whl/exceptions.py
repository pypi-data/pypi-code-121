"""Module containing the exception class for describe-get-system proof of concept module."""


class DGSError(Exception):
    """Use to capture error DGS construction."""


class TemplateStorageError(DGSError):
    """Use to capture error for TemplateStorage."""


class AdaptorAuthenticationError(DGSError):
    """Use to capture error for adaptor connection"""


class InterpreterError(DGSError):
    """Use to capture error for interpreter"""


class NotImplementedFrameworkError(InterpreterError):
    """Use to capture error for not implement framework"""


class ComparisonOperatorError(InterpreterError):
    """Use to capture error for invalid comparison operator"""


class ConnectDeviceStatementError(InterpreterError):
    """Use to capture error for interpreting connect device statement"""


class DisconnectDeviceStatementError(InterpreterError):
    """Use to capture error for interpreting disconnect device statement"""


class ReleaseDeviceStatementError(InterpreterError):
    """Use to capture error for interpreting release device statement"""


class WaitForStatementError(InterpreterError):
    """Use to capture error for interpreting wait for statement"""


class PerformerStatementError(InterpreterError):
    """Use to capture error for performer statement"""


class VerificationStatementError(InterpreterError):
    """Use to capture error for verification statement"""


class ScriptBuilderError(InterpreterError):
    """Use to capture error for building test script"""


class DurationArgumentError(InterpreterError):
    """Use to capture error for wait_for function"""


class ConvertorTypeError(InterpreterError):
    """Use to capture convertor argument for filter method"""


class TemplateReferenceError(InterpreterError):
    """Use to capture template reference for filter method"""


class UtilsParsedTemplateError(InterpreterError):
    """Use to capture error for parsing template in utils"""


class ReportError(DGSError):
    """Use to capture error for report generation in report.py"""
