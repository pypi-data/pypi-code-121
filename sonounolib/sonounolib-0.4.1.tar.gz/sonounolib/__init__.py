"""The sonoUno library.

This library provides sonification components to construct transforms.
"""
# from importlib.metadata import version

from streamunolib import exposed, hidden, media_type

from .notes import asfrequency
from .tracks import Track

__all__ = [
    'Track',
    'asfrequency',
    'exposed',
    'hidden',
    'media_type',
]

# __version__ = version('sonounolib')
