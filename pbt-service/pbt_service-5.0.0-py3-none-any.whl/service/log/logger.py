"""Logger exceptions, hooks and etc."""

import sys

import logging

from logging import Logger, LogRecord, getLogger as new_log, config  # noqa
from logging_json import JSONFormatter
from logging_json._formatter import (  # noqa
    _value as formatter_value,  # noqa
    _extra_attributes as log_extra_attrs,  # noqa
    default_converter,
)
from yaml import safe_load, YAMLError
from tblib import Traceback


blank_config = {
    'version': 1,
    'disable_existing_loggers': False,
}


def setup_logger(config_path: str, debug: bool = True):
    """Setup logger."""
    with open(config_path) as _file:
        try:
            log_config = safe_load(_file)
        except (YAMLError, FileNotFoundError) as _exc:
            print(f'Fail load log config: {config_path} - {_exc}')
            log_config = blank_config
        finally:
            config.dictConfig(log_config)
            logging.root.setLevel(logging.DEBUG if debug else logging.ERROR)
            return log_config


def except_logging(exc_type, exc_value, exc_traceback):  # noqa
    """Logging exceptions."""
    logging.exception('Uncaught exception', exc_info=exc_value)


sys.excepthook = except_logging


__all__ = (
    'new_log',
    'setup_logger',
    'except_logging',
    'Traceback',
    'config',
    'LogRecord',
    'Logger',
    'JSONFormatter',
    'formatter_value',
    'default_converter',
    'log_extra_attrs',
)
