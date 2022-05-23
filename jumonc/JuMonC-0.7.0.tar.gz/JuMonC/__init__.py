"""
JuMonC is a programm that lets you monitor and control you simulation using the provided REST-API.

Further informaton can be found in the README.md.
The application cmd arguments can be found in doc/CMD/Parameters.md
The REST API is documented with openapi, and rendered well by gitlab on:
https://gitlab.jsc.fz-juelich.de/witzler1/jumonc/-/blob/CI_fixes/doc/REST_API/openapi.yaml
"""


import logging
import sys


from JuMonC import settings
from JuMonC._version import __version__


__all__ = ["settings", "__version__", "setup_logging", "reset_logging"]

def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout if settings.LOG_STDOUT else sys.stderr)
    formatter = logging.Formatter(settings.LOG_PREFIX + settings.LOG_FORMAT)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(settings.LOG_LEVEL)
    
    fileHandler = logging.FileHandler('JuMonC.log')
    fileHandler.setFormatter(formatter)
    logging.getLogger().addHandler(fileHandler)


setup_logging()


def reset_logging() -> None:
    logger = logging.getLogger()
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
    setup_logging()
