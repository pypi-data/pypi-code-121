import os
import platform
from pathlib import Path
from typing import Literal

OS: Literal['Windows', 'Linux', 'Darwin', 'Java', ''] = platform.system()  # noqa


def is_windows() -> bool:
    """
    :return: true if running inside a windows OS
    """
    return OS == 'Windows'


def is_executable(file: Path) -> bool:
    """
    :param file: the file to test
    :return: true if the given [file] is executable (os independent)
    """
    if OS == 'Windows':
        return file.suffix == '.exe'
    return os.access(str(file), os.X_OK)
