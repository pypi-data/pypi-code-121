"""
Module containing the root library logger for the wai.common library.
"""
import logging

from ._standard_library_root_logger import create_standard_library_root_logger

# The cached root logger for wai.common
_root_logger: logging.Logger = create_standard_library_root_logger("wai.common")


def root_logger() -> logging.Logger:
    """
    Gets the root logger for the library.

    :return:    The root logger.
    """
    return _root_logger
