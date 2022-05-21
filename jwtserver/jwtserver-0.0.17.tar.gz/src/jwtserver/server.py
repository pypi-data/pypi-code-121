import logging
import sys
import uvicorn
from loguru import logger


def enable_logger(sink=sys.stderr, level='WARNING'):
    logging.basicConfig(level=logging.DEBUG)
    logger.configure(handlers=[{'sink': sink, 'level': level}])
    logger.enable('aria2p')


def dev(host='localhost', port=5000, log_level='info'):
    enable_logger(level=log_level.upper())
    uvicorn.run('jwtserver.app:app', host=host, port=port, log_level=log_level)
