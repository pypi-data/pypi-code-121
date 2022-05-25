import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from .cch import CCH  # noqa
