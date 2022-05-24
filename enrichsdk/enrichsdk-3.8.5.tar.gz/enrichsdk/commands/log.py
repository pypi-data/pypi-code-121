import os
import logging
import click
from logging.config import dictConfig


def logging_start(filename=None):

    default_filename = "ext://sys.stderr"
    if filename is None:
        filename = default_filename
    elif isinstance(filename, str):
        try:
            os.makedirs(os.path.dirname(filename))
        except:

            pass
        filename = open(filename, "a")

    # logging.basicConfig(filename='example.log',level=logging.DEBUG)
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "basic": {
                    "class": "logging.Formatter",
                    "datefmt": "%I:%M:%S",
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                },
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "basic",
                    "level": "DEBUG",
                    "stream": default_filename,
                },
                "app": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": "DEBUG",
                    "stream": filename,
                },
            },
            "loggers": {
                "": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
                "default": {
                    "level": "DEBUG",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "app": {"level": "DEBUG", "handlers": ["app"], "propagate": False},
            },
            "root": {
                "level": "DEBUG",
                #'handlers': ['app', 'console'],
                "handlers": ["app"],
            },
        }
    )


def logging_end():
    logging.shutdown()


def logging_clear():
    for h in logging._handlers.copy():
        logging.removeHandler(h)
        h.flush()
        h.close()
