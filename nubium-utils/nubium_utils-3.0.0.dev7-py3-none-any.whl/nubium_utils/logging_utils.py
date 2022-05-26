import sys
import logging
from .general_runtime_vars import default_env_vars


def _init_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(_get_loglevel())

    handler.setFormatter(
        logging.Formatter(
            "{process} - {filename:15} - {asctime} - {name} - {levelname} - {message}",
            style="{"
        )
    )
    return handler


def _get_loglevel():
    return default_env_vars()['NU_LOGLEVEL']


def init_logger(name='nubium-utils'):
    logger = logging.getLogger(name)
    logger.setLevel(_get_loglevel())
    logger.addHandler(_init_handler())
    logger.propagate = False
    return logger
