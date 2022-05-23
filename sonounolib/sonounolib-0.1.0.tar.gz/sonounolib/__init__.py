"""The sonoUno library.

This library provides sonification components to construct transforms.
"""
# from importlib.metadata import version

from .notes import asfrequency
from .tracks import Track

__all__ = [
    'Track',
    'asfrequency',
]

# __version__ = version('sonounolib')
