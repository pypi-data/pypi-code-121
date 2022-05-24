import logging
from logging import handlers
import sys
import os

from TweetAnalysis.config.core import PACKAGE_ROOT

FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"
)


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = logging.handlers.TimedRotatingFileHandler(os.getcwd() + "/logs.log")
    file_handler.setFormatter(FORMATTER)
    return file_handler

def get_socket_handler():
    socket_handler = handlers.SocketHandler(host='localhost', port=9999)
    socket_handler.setFormatter(FORMATTER)
    return socket_handler


def get_logger(logger_name):

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler())
    logger.propagate = False

    return logger