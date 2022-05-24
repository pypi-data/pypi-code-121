"""
CFFI loader for Judy.
"""

__version__ = "0.9.0"

from judyz_cffi.internal import _load

_load()

from .exceptions import JudyError  # noqa
from .judy1 import *  # noqa
from .judyl import *  # noqa
from .judysl import *  # noqa
