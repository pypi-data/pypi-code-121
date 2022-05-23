"""
Inits the log framework.
"""

import logging
import os
import sys
import time
from contextlib import contextmanager

from opentelemetry.instrumentation.logging import LoggingInstrumentor

from clearcut.otlputils import get_tracer

LOGGER_NAME_LENGTH = 30

NOISY_LIBRARIES = ["aio_pika"]


class ShortNameFilter(logging.Filter):
    """Shorten the logger name (if necessary) to make printing easier to read."""

    @staticmethod
    def _short_logger_name(name):
        # Split the name by `.`, and from left-to-right, shrink each piece to the first letter, until we're short enough
        if len(name) <= LOGGER_NAME_LENGTH:
            return name
        else:
            name_components = name.split(".")
            for idx, comp in enumerate(name_components):
                # reduce the given component
                name_components[idx] = comp[0]

                # short enough yet?
                if len(".".join(name_components)) <= LOGGER_NAME_LENGTH:
                    break

            return ".".join(name_components)

    def filter(self, record):
        record.shortname = self._short_logger_name(record.name)
        return True


def init_logging():
    # Was a log level set?
    try:
        loglevel = os.environ.get("LOGLEVEL", "INFO").upper()
        loglevel = getattr(logging, loglevel)
    except Exception as e:
        loglevel = logging.INFO

    # OTLP instrumentation
    _ = get_tracer(__name__)
    LoggingInstrumentor().instrument(set_logging_format=False)

    # sysout handler for human-readable
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        logging.Formatter(
            "{asctime} [{levelname:7}] ({shortname:"
            + str(LOGGER_NAME_LENGTH)
            + "."
            + str(LOGGER_NAME_LENGTH)
            + "}) / [trace={otelTraceID} span={otelSpanID}] | {message}",
            style="{",
        )
    )
    stream_handler.addFilter(ShortNameFilter())

    # add handler to logger
    root_logger = logging.getLogger()
    root_logger.addFilter(ShortNameFilter())
    root_logger.addHandler(stream_handler)

    root_logger.setLevel(loglevel)

    # Some customizations
    # log some known noisy libraries at warning level
    for lib in NOISY_LIBRARIES:
        logging.getLogger(lib).setLevel(logging.WARNING)


init_logging()


@contextmanager
def log_block(name: str, logger: logging.Logger, debug: bool = True):
    """
    Allows for easy logging of a block of code, with performance tracked automatically. Logs at debug level, unless debug=False, in which
    case it logs at info level.
    """
    logger_fn = logger.debug if debug else logger.info
    logger_fn(f"Enter: [{name}]")

    start = time.perf_counter()
    yield

    duration = time.perf_counter() - start
    logger_fn(f"Exit: [{name}]. Duration: {duration:.1f}s")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
