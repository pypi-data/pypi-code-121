import sys
import logging
import os

import structlog
from pythonjsonlogger import jsonlogger


def add_service(_, __, event_dict):
    event_dict["service"] = os.environ.get("service", "")
    return event_dict

def setup_logging(level=logging.INFO):

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(jsonlogger.JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    logger = structlog.get_logger()

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            add_service,
            structlog.processors.TimeStamper(
                fmt="iso",
                utc=True,
                key="timestamp"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return logger
