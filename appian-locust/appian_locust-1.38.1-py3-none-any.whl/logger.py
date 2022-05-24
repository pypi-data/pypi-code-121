import logging

"""
Custom logger module borrowing all the functionality of original python's logger module.
Additionally it sets the format of the log to '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

Make sure to name the logger "log" or anything other than "logger" on the receiving script to ensure Mypy conformity

Example:

    >>> from appian_locust import logger
    >>> log = logger.getLogger(__file__)
    >>> log.info("Info message")

"""

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def getLogger(name: str = None) -> logging.Logger:
    """

    Args:
        name(str, optional): Name of the logger. it is common practice to use file name here but it can be anything.

    Returns: logger object

    """
    return logging.getLogger(name)
