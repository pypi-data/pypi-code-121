# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from .azureml_error import AzureMLException


class ValidationException(AzureMLException):
    """Exception raised when validation on user input fails."""

    def __init__(self, exception_message, **kwargs):
        super().__init__(exception_message=exception_message, **kwargs)


class InvalidOperationException(ValidationException):
    """Exception raised when an attempt is made to perform an illegal operation."""

    def __init__(self, exception_message, **kwargs):
        super().__init__(exception_message=exception_message, **kwargs)


class InvalidValueException(ValidationException):
    """
    Exception raised when an argument is expected to have a non-null (or an accepted) value,
    but is actually null (or something else).
    """

    def __init__(self, exception_message, **kwargs):
        super().__init__(exception_message=exception_message, **kwargs)


class InvalidTypeException(ValidationException):
    """
    Exception raised when an argument is expected to be of one type, but is actually something else.
    """

    def __init__(self, exception_message, **kwargs):
        super().__init__(exception_message=exception_message, **kwargs)


class PredictionException(AzureMLException):
    """
    Exception related to prediction in external pipelines and transformers.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """
    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new PredictionException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)
