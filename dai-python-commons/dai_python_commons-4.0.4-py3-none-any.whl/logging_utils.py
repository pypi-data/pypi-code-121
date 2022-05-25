"""Functions for logging"""
import itertools
import json
import sys
from typing import Dict

from loguru import logger
from loguru._better_exceptions import ExceptionFormatter
from loguru._handler import Message


class LoggingUtils:  # pylint: disable=too-few-public-methods
    """
    Class that provides useful functions for logging
    """
    exception_formatter = ExceptionFormatter()

    @staticmethod
    def get_logger(name: str, level: str = "INFO") -> logger:
        """Returns a logger object"""
        logger.remove()
        logger.configure(extra={"name": name})
        logger.add(LoggingUtils._sink, level=level)

        return logger

    @staticmethod
    def _sink(message: Message) -> None:
        simplified = LoggingUtils._formatter(message.record)
        print(json.dumps(simplified), file=sys.stderr)

    @staticmethod
    def _formatter(record: Dict[str, any]) -> Dict[str, any]:
        log_record = {
            "name": record["extra"]["name"],
            "level": record["level"].name,
            "line": record["line"],
            "file": record["file"].name,
            "message": record["message"],
            "time": record["time"].isoformat(),
        }

        if record.get("exception"):
            log_record["exception"] = list(
                # chain.from_iterable flattens list of lists
                itertools.chain.from_iterable(
                    e.split('\n')
                    for e in LoggingUtils.exception_formatter.format_exception(*record["exception"]) if e
                )
            )

        return log_record
