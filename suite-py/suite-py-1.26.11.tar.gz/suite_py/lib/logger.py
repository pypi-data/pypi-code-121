# -*- encoding: utf-8 -*-
import logging

import logzero
from logzero import logger as _logger

DEFAULT_FORMAT = "%(color)s[%(levelname)1.4s]%(end_color)s %(message)s"
# Set a custom formatter
formatter = logzero.LogFormatter(fmt=DEFAULT_FORMAT)
logzero.setup_default_logger(formatter=formatter)
_logger.setLevel(logging.INFO)


def setLevel(level):
    _logger.setLevel(level)


def debug(message):
    _logger.debug(message)


def info(message):
    _logger.info(message)


def warning(message):
    _logger.warning(message)


def error(message):
    _logger.error(message)
