##
# File: LogFilterUtils.py
# Date: 29-Jun-2020 jdw
#
# Pre-filter for Gunicorn/Uvicorn health check requests -
##
# pylint: disable=E1101
import logging

logger = logging.getLogger(__name__)


class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage().find("/healthcheck") == -1


class LogFilterUtils(object):
    def __init__(self):
        pass

    def addFilters(self):
        logger.debug("Current loggers are: %r", [name for name in logging.root.manager.loggerDict])  # pylint: disable=E1101
        for name in logging.root.manager.loggerDict:  # pylint: disable=E1101
            if any(x in name for x in ["uvicorn", "gunicorn"]):
                logger.debug("Add filter to logger %r", name)
                loggerT = logging.getLogger(name)
                loggerT.addFilter(HealthCheckFilter())
