"""
it4ifree portal clients logger
"""

import logging

LOGGER = logging.getLogger(__package__)
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.ERROR)
LOGGER.addHandler(CONSOLE_HANDLER)
