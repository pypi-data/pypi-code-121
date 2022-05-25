# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Package containing modules used in automated machine learning.
"""

__path__ = __import__('pkgutil').extend_path(__path__, __name__)    # type: ignore

try:
    from ._version import selfver as SELFVERSION
    from ._version import ver as VERSION

    __version__ = VERSION
except ImportError:
    VERSION = "0.0.0+dev"
    SELFVERSION = VERSION
    __version__ = VERSION
