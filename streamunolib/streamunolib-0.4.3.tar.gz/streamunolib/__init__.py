"""The streamUno library.

This library provides generic components to construct transforms and decorators
to annotate these components.
"""
from importlib.metadata import version

from .decorators import exposed, hidden
from .media_types import media_type

__all__ = [
    'exposed',
    'hidden',
    'media_type',
]

__version__ = version('streamunolib')
