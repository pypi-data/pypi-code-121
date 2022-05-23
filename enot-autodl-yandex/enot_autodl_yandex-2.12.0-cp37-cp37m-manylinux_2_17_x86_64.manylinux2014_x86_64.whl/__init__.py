from pathlib import Path

from enot.logging.logging import logging_config

logging_config()


def _get_version() -> str:
    with Path(__file__).parent.joinpath('VERSION').open('r') as version_file:
        version = version_file.read().strip()

    return version


__version__ = _get_version()

