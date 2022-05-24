import logging
from logging.config import dictConfig

logconfig = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "basic": {
            "class": "logging.Formatter",
            "datefmt": "%I:%M:%S",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "expanded": {
            "class": "logging.Formatter",
            "format": "%(asctime)s - %(name)s - %(transform)s - %(levelname)s - %(message)s%(data)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "basic",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "app": {
            "class": "logging.StreamHandler",
            "formatter": "expanded",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"level": "INFO", "handlers": ["console"], "propagate": False},
        "default": {"level": "INFO", "handlers": ["console"], "propagate": False},
        "app": {"level": "DEBUG", "handlers": ["app"], "propagate": False},
    },
    "root": {"level": "WARN", "handlers": ["console"]},
}


def setup_logging():
    dictConfig(logconfig)

    for name in [
        "kazoo.client",
        "pykafka.simpleconsumer",
        "pykafka.handlers",
        "pykafka.balancedconsumer",
        "pykafka.connection",
        "pykafka.membershipprotocol",
        "pykafka.cluster",
        "pykafka.topic",
        "matplotlib.pyplot",
        "asyncio",
    ]:
        logging.getLogger(name).disabled = True
