import logging
import sys
from typing import List


def setup_log(level=logging.DEBUG, handlers: List[logging.Handler] = None) -> None:
    if not handlers:
        handlers = []
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(get_format())
    logging.basicConfig(level=level, handlers=[handler] + handlers)


def get_format() -> logging.Formatter:
    return logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s] - %(message)s')


def get_json_format() -> logging.Formatter:
    return logging.Formatter(
        "{'time':'%(asctime)s', 'name': '%(name)s', 'func': '%(funcName)s', 'level': '%(levelname)s', "
        "'message': '%(message)s'}"
    )
