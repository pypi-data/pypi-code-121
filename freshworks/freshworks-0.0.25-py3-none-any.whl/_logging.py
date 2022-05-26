import logging.config
import os
from pathlib import Path
from typing import Any
from typing import Dict


logs_path = Path(__file__).parent.parent / "logs"
logs_path.mkdir(exist_ok=True)
log_file = logs_path / Path(__file__).with_suffix(".log").name


LOGGING_CONFIG: Dict[str, Any] = dict(
    version=1,
    disable_existing_loggers=False,
    root=dict(
        level=logging.DEBUG,
        handlers=["file_handler"],
    ),
    formatters={
        "default": {
            "date_format": "%Y-%m-%dT%H:%M:%S+0000%z",
            "format": "{asctime} - {name} - {levelname:<8} - {message}",
            "style": "{",
            "validate": True,
        }
    },
    handlers={
        "file_handler": {
            "level": logging.DEBUG,
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": log_file,
        },
    },
    loggers={},
)


def get_logger(config: Dict) -> logging.Logger:
    """Get logger based on config"""

    logging.config.dictConfig(LOGGING_CONFIG)

    # Default Values
    if config.get("name") is None:
        name = "root"

    # Config Values
    name = config["name"]

    logger = logging.getLogger(name)

    # Formatter
    date_format = "%Y-%m-%dT%H:%M:%S%z"
    message_format = "{asctime} - {name} - {levelname:<8} - {message}"
    formatter = logging.Formatter(
        datefmt=date_format,
        style="{",
        fmt=message_format,
        validate=True,
    )

    # File Handler
    file_handler = logging.FileHandler(Path(__file__).with_suffix(".log"))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Debug
    debug = os.environ.get("FRESHDESK_DEBUG") == "1"
    if debug:

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)

    return logger
