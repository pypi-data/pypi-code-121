"""
UFCPY
~~~~~~~~
A wrapper for the UFC website

:copyright: 2021-present YoungTrep
:license: MIT. See LICENSE for more details 
"""

from .Fighter import *
from .Champion import *
from .exceptions import *

__title__ = "ufcpy"
__summary__ = "A wrapper for the UFC website"
__author__ = "Oliver"
__version__ = "2.0"
__license__ = "MIT"
__copyright__ = "2021-present YoungTrep"


def get_version():
    return __version__
