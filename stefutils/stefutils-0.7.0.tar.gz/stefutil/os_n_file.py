"""
os-related
"""

import os
import pathlib
from typing import Union


__all__ = ['get_hostname', 'stem']


def get_hostname() -> str:
    return os.uname().nodename


def stem(path: Union[str, pathlib.Path], keep_ext=False) -> str:
    """
    :param path: A potentially full path to a file
    :param keep_ext: If True, file extensions is preserved
    :return: The file name, without parent directories
    """
    return os.path.basename(path) if keep_ext else pathlib.Path(path).stem
