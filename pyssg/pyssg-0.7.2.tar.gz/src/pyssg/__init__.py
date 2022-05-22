from logging import Logger, StreamHandler, getLogger, INFO

from .pyssg import main
from .per_level_formatter import PerLevelFormatter


# since this is the root package, setup the logger here
__LOG_LEVEL: int = INFO
log: Logger = getLogger(__name__)
log.setLevel(__LOG_LEVEL)
ch: StreamHandler = StreamHandler()
ch.setLevel(__LOG_LEVEL)
ch.setFormatter(PerLevelFormatter())
log.addHandler(ch)

# not meant to be used as a package, so just give main
__all__ = ['main']