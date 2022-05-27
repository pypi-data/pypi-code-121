import os
import logging


def set_up(log_level=None):
    """
    Set up logging using log_level parameter 
    if not specified attempt to use environment variable
    otherwise use ERROR
    :return: logger
    """
    logger = logging.getLogger()
    if log_level != None:
        logger.setLevel(logging._nameToLevel[log_level.upper()])
    else:
        try:
            log_level = os.environ['LOG_LEVEL']
            logger.setLevel(logging._nameToLevel[log_level.upper()])
        except KeyError:
            logger.setLevel(logging.ERROR)

    return logger
