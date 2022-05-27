"""Gear testing suite and utilities"""
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

try:
    import unittest

    import pytest
except (ImportError, ModuleNotFoundError):
    raise RuntimeError("Need to have pytest and unittest installed to use this module.")

from .files import *
from .gears import *
from .hierarchy import *
from .sdk import *
from .utils import *
