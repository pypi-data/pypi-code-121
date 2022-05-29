import logging

from pydmt.static import LOGGER_NAME


def get_logger():
    """
    This function returns the logger for pydmt
    """
    return logging.getLogger(LOGGER_NAME)
