"""
Module for typing-related types, methods, etc.
"""
from typing import TypeVar, Callable

# Standard unbounded type variable
T = TypeVar("T")

# Type for predicate functions
Predicate = Callable[[T], bool]
