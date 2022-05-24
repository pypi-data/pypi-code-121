"""Exceptions file for eox-audit-model.

Classes:
    EoxAuditModelException: General exceptions for eox-audit-model.
    EoxAuditModelInvalidMethod: Exception raises when a method is not valid.
    EoxAuditModelInvalidParameters: Exception raises when the parameters are not valid.
"""


class EoxAuditModelException(Exception):
    """EoxAuditModelException used for general exception and subclasses."""


class EoxAuditModelInvalidMethod(EoxAuditModelException):
    """Raises when the audited method is not valid."""


class EoxAuditModelInvalidParameters(EoxAuditModelException):
    """The parameters, used in a call, are not valid."""
