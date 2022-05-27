"""Typed wrappers around the Bitfount REST api."""
from typing import List

from bitfount.hub.api import (
    PRODUCTION_AM_URL,
    PRODUCTION_HUB_URL,
    BitfountAM,
    BitfountHub,
    PodPublicMetadata,
)
from bitfount.hub.authentication_flow import BitfountSession
from bitfount.hub.exceptions import PodDoesNotExistError
from bitfount.hub.helper import get_pod_schema

__all__: List[str] = [
    "BitfountAM",
    "BitfountHub",
    "BitfountSession",
    "PodDoesNotExistError",
    "PodPublicMetadata",
    "PRODUCTION_AM_URL",
    "PRODUCTION_HUB_URL",
    "get_pod_schema",
]

# See top level `__init__.py` for an explanation
__pdoc__ = {}
for _obj in __all__:
    __pdoc__[_obj] = False
