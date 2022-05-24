"""mfire.utils module

This module manages the processing of common modules

"""

from mfire.utils.json_diff import dict_diff, json_diff
from mfire.utils.json_utils import JsonFile
from mfire.utils.hash import MD5
from mfire.utils.parallel import Parallel, current_process

__all__ = [
    "JsonFile",
    "MD5",
    "dict_diff",
    "json_diff",
    "Parallel",
    "current_process",
]
