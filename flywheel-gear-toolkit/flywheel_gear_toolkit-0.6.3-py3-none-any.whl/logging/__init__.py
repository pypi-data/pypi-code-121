"""Module for default logging configuration.

This module utilizes an optionally provided configuration dictionary to
update default logging configuration.

Alternatives to updating the default logging templates can be
    >>> log_level = logging.INFO # logging.DEBUG, etc.
    >>> log_format = '[%(levelname)8s] %(message)s'
    >>> log_dtfmt = ''
    >>> logging.basicConfig(level=log_level, format=log_format, datefmt=log_dtfmt)

Or,
    >>> logging.config.dictConfig(config)

For a dictionary logging configuration, ``config``, as below.

For more in-depth information on python logging, see
https://docs.python.org/3.6/library/logging.html.
"""

import collections.abc
import json
import logging
import logging.config
import os.path as op

log = logging.getLogger(__name__)


class OutFilter(logging.Filter):
    """
    Class with single boolean function for filtering non-error log records
    """

    def __init__(self, param=None):
        self.param = param

    def filter(self, record):
        return record.levelno in [logging.INFO, logging.WARNING]


class ErrFilter(logging.Filter):
    """
    Class with single boolean function for filtering error log records
    """

    def __init__(self, param=None):
        self.param = param

    def filter(self, record):
        return record.levelno not in [logging.INFO, logging.WARNING]


def _recursive_update(template_dict, update_dict):
    """Update dictionary `template_dict` with key/value from dictionary `update_dict`.

    The keys of `update_dict` are iterated through. If the value of `template_dict` key
    is itself a dictionary the function is recursively called on those dictionaries at
    that level for both `template_dict` and `update_dict`. If the dictionary
    `update_dict` has keys that are not present in `template_dict`, they will be added
    recursively.

    Args:
        template_dict (dict): The dictionary to be updated.

        update_dict (dict): The dictionary containing update keys. If update_dict is
            template_dict subset of template_dict, it will update just those keys.
            Otherwise, it will add any keys in update_dict not found in template_dict.
    """

    for k, v in update_dict.items():
        if isinstance(v, collections.abc.Mapping):
            _recursive_update(template_dict.get(k, {}), v)
        else:
            template_dict[k] = update_dict[k]


def configure_logging(default_config_name="info", update_config=None):
    """Configures logging with default settings or a dictionary of log settings.

    Configures the logging for the gear-toolkit module using one
    of either two default json templates (`info`, `debug` -- see below).
    Whichever one is used can be updated with an optional `update_config`
    dictionary.

    Logging sent to DEBUG, ERROR, and CRITICAL will be filtered and sent to stderr.

    Logging sent to INFO and WARNING will be filtered and sent to stdout.

    Args:
        default_config_name (str, optional): A string, 'info' or 'debug', indicating
            the default template to use. Defaults to 'info'.
        update_config (dict, optional): A dictionary containing the keys,
            subkeys, and values of the templates to update.
            Defaults to `None`.

    Example:
        .. code-block:: python

            config = {
                "formatters": {
                    "gear": {
                        "format": "[TEST] %(levelname)4s %(message)s"
                    }
                }
            }
            configure_logging(update_config = config)


        will update the ['formatters']['gear']['format'] value in the `info`.
        Default configuration below.

    Note:
        Default logging configuration dictionaries are stored in
        ``defaults/<prefix>.json``.

        `info`:

        .. code-block:: json

            {
                "version": 1,
                "filters": {
                    "out_filter": {
                        "()": "PlaceHolder",
                        "param": "noshow"
                    },
                    "err_filter": {
                        "()": "PlaceHolder",
                        "param": "noshow"
                    }
                },
                "formatters": {
                    "gear": {
                        "format":"[%(asctime)s - %(levelname)s - %(name)s] %(message)s",
                        "datefmt": "%Y%m%d"
                    }
                },
                "handlers": {
                    "gear": {
                        "level":"INFO",
                        "formatter": "gear",
                        "class":"logging.StreamHandler"
                    }
                },
                "loggers": {
                    "": {
                        "handlers": ["gear"],
                        "level":"INFO"
                    }
                },
                "disable_existing_loggers": false
            }

        `debug`:

        .. code-block:: json

            {
                "version": 1,
                "filters": {
                    "out_filter": {
                        "()": "PlaceHolder",
                        "param": "noshow"
                    },
                    "err_filter": {
                        "()": "PlaceHolder",
                        "param": "noshow"
                    }
                },
                "formatters": {
                    "gear": {
                        "format":  "[%(asctime)s - %(levelname)s - %(name)s:%(lineno)d] %(message)s",
                        "datefmt": "%Y%m%d"
                    }
                },
                "handlers": {
                    "gear": {
                        "level":"DEBUG",
                        "formatter": "gear",
                        "class":"logging.StreamHandler"
                    }
                },
                "loggers": {
                    "": {
                        "handlers": ["gear"],
                        "level":"DEBUG"
                    }
                },
                "disable_existing_loggers": false
            }
    """

    available_names = ["info", "debug"]

    if default_config_name not in available_names:
        log.warning(
            "The value of %s is not in %s. Reverting to 'info'.",
            default_config_name,
            available_names,
        )
        default_config_name = "info"

    json_file = op.join(op.dirname(__file__), "defaults", default_config_name + ".json")

    with open(json_file, "r") as f:
        config = json.load(f)

    if update_config:
        _recursive_update(config, update_config)
    if config.get("filters"):
        if config["filters"].get("out_filter"):
            config["filters"]["out_filter"]["()"] = OutFilter
        if config["filters"].get("err_filter"):
            config["filters"]["err_filter"]["()"] = ErrFilter

    logging.config.dictConfig(config)

    log.info("Log level is %s", logging.getLevelName(logging.root.level))
