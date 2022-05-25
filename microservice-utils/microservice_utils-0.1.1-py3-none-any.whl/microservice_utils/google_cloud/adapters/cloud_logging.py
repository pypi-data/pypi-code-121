"""
Adapted from:
https://github.com/googleapis/python-logging/blob
/6a1f19d9929137d4a5ec6bd4d758a16ec5b284e1/google/cloud/logging_v2/handlers
/container_engine.py
"""
import json
import logging
import math
import sys

import ulid

from microservice_utils.constants import LOG_FORMATTER


def format_stackdriver_json(record, message) -> str:
    """Helper to format a LogRecord in Stackdriver fluentd format.
    Returns:
        str: JSON str to be written to the log file.
    """
    subsecond, second = math.modf(record.created)

    payload = {
        "message": message,
        "timestamp": {"seconds": int(second), "nanos": int(subsecond * 1e9)},
        "thread": record.thread,
        "severity": record.levelname,
    }

    return json.dumps(payload, ensure_ascii=False)


class ContainerEngineHandler(logging.StreamHandler):
    """Handler to format log messages the format expected by GKE fluent.
    This handler is written to format messages for the Google Container Engine
    (GKE) fluentd plugin, so that metadata such as log level are properly set.
    """

    def __init__(self, *, name=None, stream=None):
        """
        Args:
            name (Optional[str]): The name of the custom log in Cloud Logging.
            stream (Optional[IO]): Stream to be used by the handler.
        """
        super(ContainerEngineHandler, self).__init__(stream=stream)
        self.name = name

    def format(self, record) -> str:
        """Format the message into JSON expected by fluentd.
        Args:
            record (logging.LogRecord): The log record.
        Returns:
            str: A JSON string formatted for GKE fluentd.
        """
        message = super(ContainerEngineHandler, self).format(record)
        return format_stackdriver_json(record, message)


def generate_trace_id() -> str:
    return ulid.new().str


def set_up_cloud_logging(
    log_level: str, formatter: logging.Formatter = None
) -> logging.Logger:
    log_level = log_level.upper()
    logger = logging.getLogger()
    logger.setLevel(log_level)

    sh = ContainerEngineHandler(stream=sys.stdout)
    sh.setLevel(log_level)
    sh.setFormatter(formatter or LOG_FORMATTER)

    logger.addHandler(sh)

    return logger
