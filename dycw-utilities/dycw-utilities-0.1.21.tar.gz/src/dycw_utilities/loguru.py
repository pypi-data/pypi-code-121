from sys import stdout

from loguru import logger

from dycw_utilities.logging import LogLevel
from dycw_utilities.pathlib import PathLike


def setup_loguru(*, name: PathLike = "log") -> None:
    logger.remove()

    format = (
        "<green>{time:YYYY-MM-DD}</green>"
        " "
        "<bold><green>{time:HH:mm:ss}</green></bold>"
        "."
        "{time:SSS}"
        "  "
        "<cyan>{process.name}</cyan>-{process.id}"
        "  "
        "<green>{name}</green>-<cyan>{function}</cyan>"
        "  "
        "<bold><level>{level.name}</level></bold>"
        "\n"
        "{message}"
    )

    _ = logger.add(stdout, level=LogLevel.INFO, format=format, enqueue=True)
    _ = logger.add(
        name,
        level=LogLevel.DEBUG,
        enqueue=True,
        rotation="10 MB",
        retention="1 week",
    )
