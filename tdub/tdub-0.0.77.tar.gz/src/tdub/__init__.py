"""tW analysis tools."""

from .version import version as __version__  # noqa


def setup_logging():
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(name)-15s %(funcName)-28s %(levelname)-9s    %(message)s",
    )
    logging.addLevelName(
        logging.WARNING,
        f"\033[1;31m{logging.getLevelName(logging.WARNING)}\033[1;0m",
    )
    logging.addLevelName(
        logging.ERROR, f"\033[1;35m{logging.getLevelName(logging.ERROR)}\033[1;0m"
    )
    logging.addLevelName(
        logging.INFO, f"\033[1;32m{logging.getLevelName(logging.INFO)}\033[1;0m"
    )
    logging.addLevelName(
        logging.DEBUG, f"\033[1;34m{logging.getLevelName(logging.DEBUG)}\033[1;0m"
    )
