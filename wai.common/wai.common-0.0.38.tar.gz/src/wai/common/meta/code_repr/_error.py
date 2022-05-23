"""
Module containing error types for when problems occur during
handling of code representations.
"""
from typing import Any


class CodeRepresentationError(Exception):
    """
    Type of error occurring when there is a problem getting the
    code-representation of a value.
    """
    pass


class IsNotCodeRepresentableValue(CodeRepresentationError):
    """
    Error for when a value is not code-representable.
    """
    def __init__(self, value: Any):
        super().__init__(f"Value '{value}' is not code-representable")


class IsNotCodeRepresentableType(CodeRepresentationError):
    """
    Error for when a type is not code-representable.
    """
    def __init__(self, cls: type):
        super().__init__(f"Type '{cls.__qualname__}' is not code-representable")


class ConflictingImports(CodeRepresentationError):
    """
    Error for when combining import dictionaries and there is
    more than one import under a given identifier.
    """
    def __init__(self, identifier: str, import_code_1: str, import_code_2: str):
        super().__init__(f"Multiple conflicting imports with name '{identifier}'\n"
                         f"{import_code_1}\n"
                         f"<->\n"
                         f"{import_code_2}")
