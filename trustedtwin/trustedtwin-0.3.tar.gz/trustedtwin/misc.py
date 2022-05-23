"""Misc class and operations for API client"""
from enum import Enum, auto


class RESTMethod(str, Enum):
    """REST Method used in TT API"""

    GET = auto()
    POST = auto()
    PATCH = auto()
    DELETE = auto()

    def __str__(self) -> str:
        """Override default behavior"""
        return str(self.name)
