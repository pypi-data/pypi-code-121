import logging
import sys
from logging.handlers import RotatingFileHandler, SysLogHandler

from pathlib import Path
from typing import Optional

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s:%(message)s"
DATE_FORMAT = "%d-%b-%Y %H:%M:%S"

logger = logging.getLogger(__name__)


def setupPeekLogger(serviceName: Optional[str] = None):
    logging.basicConfig(
        stream=sys.stdout, format=LOG_FORMAT, datefmt=DATE_FORMAT, level=logging.DEBUG
    )

    if serviceName:
        updatePeekLoggerHandlers(serviceName)


def updatePeekLoggerHandlers(
    serviceName: Optional[str] = None,
    rotateSizeMb=1024 * 1024,
    rotationsToKeep=2,
    logToStdout=True,
):
    rootLogger = logging.getLogger()
    logFormatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    for handler in list(rootLogger.handlers):
        if isinstance(handler, RotatingFileHandler):
            # Setup the file logging output
            rootLogger.removeHandler(handler)

        elif not sys.stdout.isatty() and not logToStdout:
            # Remove the stdout handler
            logger.info("Logging to stdout disabled, see 'logToStdout' in config.json")
            rootLogger.removeHandler(handler)

    fileName = str(Path.home() / ("%s.log" % serviceName))

    fh = RotatingFileHandler(
        fileName, maxBytes=(1024 * 1024 * rotateSizeMb), backupCount=rotationsToKeep
    )
    fh.setFormatter(logFormatter)
    rootLogger.addHandler(fh)


def setupLoggingToSysloyServer(host: str, port: int, facility: str):
    rootLogger = logging.getLogger()
    logFormatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    logging.getLogger().addHandler(logging.StreamHandler())

    if facility not in SysLogHandler.facility_names:
        logger.info(list(SysLogHandler.facility_names))
        raise Exception("Syslog facility name is a valid facility")

    facilityNum = SysLogHandler.facility_names[facility]

    fh = SysLogHandler(address=(host, port), facility=facilityNum)
    fh.setFormatter(logFormatter)
    rootLogger.addHandler(fh)
