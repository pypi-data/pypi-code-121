"""
`embedops_cli`
=======================================================================
* Author(s): Bailey Steinfadt, Zhi Xuen Lai
"""
import logging
import logging.config
from os import path
import json
from .version import (
    __version__,
)  # Import __version__ attribute so that it is visible to the setup.cfg

LOGGING_CONFIG = path.join(path.dirname(__file__), "logging.json")
if path.exists(LOGGING_CONFIG):
    with open(LOGGING_CONFIG, "rt", encoding="ascii") as fd:
        config = json.load(fd)
    logging.config.dictConfig(config)
