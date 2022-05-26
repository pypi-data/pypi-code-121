"""
Custom Logger Library
~~~~~~~~~~~~~~~~~~~~~

Logger is a logging and metrics Python library for recording business logic.

Basic usage:
    >>> from kumuniverse.logger import Logger
    >>> logger = Logger("Yamashita API")
    >>> logger.session_id
    1e5530a9-8fad-4460-8c75-c92e73482eb1
    >>> logger.error("Hello World!")
    {
    "message": "Hello World!"
    "epoch_time": "1637054304.748814"
    "level": "ERROR"
    "microservice": "Yamashita API"
    "session_id": "1e5530a9-8fad-4460-8c75-c92e73482eb1"
    "time": "2021-11-16T09:18:24.749Z"
    "type": "Business Logic"
    }

"""
import json
import logging
import os
import re
import sys
import time
import uuid


class _JSONFormatter(logging.Formatter):
    def format(self, record):
        """
        Defines the format of the logs with a JSON annotation.
        Args:
        - record (LogRecord): contains all the information pertinent to the event being logged
        """
        string_formatted_time = time.strftime(
            "%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)
        )
        obj = {}
        obj["level"] = record.levelname
        obj["epoch_time"] = record.created
        obj["time"] = f"{string_formatted_time}.{record.msecs:3.0f}Z"
        obj["message"] = record.msg

        # If the data type logged is a dictionary, the additional key-value pairs are also included in the returned JSON object
        if hasattr(record, "extra"):
            for key, value in record.extra.items():
                obj[key] = value
        return json.dumps(obj)


class Logger:
    def __init__(self, name=None, env="dev"):
        """
        Initializes Logger library.
        Args:
        - name (string): name of the service that's using the logger
        - env (string): "dev" or "live", defaults to "dev" if None
        """
        self.name = name
        self.session_id = str(uuid.uuid4())
        self.record = {
            "microservice": self.name,
            "env": env,
            "session_id": self.session_id,
        }
        self.logger = logging.getLogger(__name__)

        # Remove default logger and override it with the defined configuration
        self.logger.propagate = False
        if self.logger.handlers:
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)

        handler = logging.StreamHandler(sys.stdout)
        formatter = _JSONFormatter()
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        if "DEBUG" in os.environ and os.environ["DEBUG"] == "true":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
            logging.getLogger("boto3").setLevel(logging.WARNING)
            logging.getLogger("botocore").setLevel(logging.WARNING)

    def _strip_lines(self, m):
        """
        Remove line breaks to ensure log statements correspond to one message only.
        Args:
        - m (string): log message
        """
        m = re.compile(r"[\t]").sub(" ", str(m))
        return re.compile(r"[\r\n]").sub("", str(m))

    def get_new_session_id(self):
        """
        Generate a new session ID for new logs.
        """
        self.session_id = str(uuid.uuid4())
        self.record["session_id"] = self.session_id

    def exception(self, e):
        """
        Log exception event.
        Args:
        - e (string): exception message
        """
        logger = self.logger
        record = self.record | {"message": self._strip_lines(e)}
        logger.exception(record)

    def debug(self, msg, log_type="Business Logic"):
        """
        Log debug event.
        Args:
        - msg (string/dictionary): debug event
        - type (string): type of log event, defaults to "Business Logic" if None
        """
        logger = self.logger
        record = (
            self.record | {"message": msg, "type": log_type}
            if isinstance(msg, str)
            else self.record | msg
        )
        logger.debug(msg=record)

    def info(self, msg, log_type="Business Logic"):
        """
        Log info event.
        Args:
        - msg (string/dictionary): info event
        - type (string): type of log event, defaults to "Business Logic" if None
        """
        logger = self.logger
        record = (
            self.record | {"message": msg, "type": log_type}
            if isinstance(msg, str)
            else self.record | msg
        )
        logger.info(msg=record)

    def warning(self, msg, log_type="Business Logic"):
        """
        Log warning event.
        Args:
        - msg (string/dictionary): warning event
        - type (string): type of log event, defaults to "Business Logic" if None
        """
        logger = self.logger
        record = (
            self.record | {"message": msg, "type": log_type}
            if isinstance(msg, str)
            else self.record | msg
        )
        logger.warning(msg=record)

    def error(self, msg, log_type="Business Logic"):
        """
        Log error event.
        Args:
        - msg (string/dictionary): error event
        - type (string): type of log event, defaults to "Business Logic" if None
        """
        logger = self.logger
        record = (
            self.record | {"message": msg, "type": log_type}
            if isinstance(msg, str)
            else self.record | msg
        )
        logger.error(msg=record)
