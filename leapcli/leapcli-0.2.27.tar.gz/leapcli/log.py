import logging
import os
from pythonjsonlogger import jsonlogger


def configure_logging():
    log_level = int(os.environ.get('LEAP_LOG_LEVEL', str(logging.ERROR)))
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(handler)
