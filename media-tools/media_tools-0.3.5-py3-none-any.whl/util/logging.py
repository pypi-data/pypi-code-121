__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import logging
from argparse import Namespace

import coloredlogs


def setup_logging(args: Namespace, fmt: str = '%(asctime)s %(levelname)s: %(message)s') -> None:
    log_level = logging.DEBUG if getattr(args, 'debug', False) else logging.INFO
    for _ in range(getattr(args, 'quiet', 0)):
        log_level += (logging.INFO - logging.DEBUG)
    coloredlogs.install(
        level=log_level, fmt=fmt,
        datefmt='%H:%M:%S'
    )
