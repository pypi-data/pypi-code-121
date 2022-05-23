#!/usr/bin/env python3

import os
import logging
from logging import Logger
# from distutils.util import strtobool
from utils_tddschn.sync.utils import strtobool
from typing import Literal

logging_format = '%(levelname)s:%(name)s:%(pathname)s:%(lineno)s:%(funcName)s:%(message)s'


def get_logger(name,
               level: int = logging.INFO,
               logging_format: str = logging_format,
               env_var_name: str = '_DEBUG',
               do_log: bool = False) -> tuple[Logger, Literal[0, 1]]:
    """ logs if TODO_DEBUG env var is true"""
    logger = logging.getLogger(name)

    _DEBUG_S: str = os.environ.get(env_var_name, '0')
    _DEBUG = strtobool(_DEBUG_S)

    if _DEBUG or do_log:
        # https://stackoverflow.com/questions/7016056/python-logging-not-outputting-anything
        logging.basicConfig(level=logging.NOTSET)
        logger.setLevel(level)
        logger.propagate = False
        ch = logging.StreamHandler()
        # ch.setLevel(logging.INFO)

        # see logrecord attributes in the doc
        formatter = logging.Formatter(logging_format)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    else:
        # logging.getLogger(__name__).addHandler(logging.NullHandler())
        logger.addHandler(logging.NullHandler())

    return logger, _DEBUG