import logging
import warnings

from hackle.commons import enums

_DEFAULT_LOG_FORMAT = '%(levelname)-8s %(threadName)s %(asctime)s %(filename)s:%(lineno)s:%(message)s'


def reset_logger(name, level=None, handler=None):
    if level is None:
        level = logging.INFO
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = handler or logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_DEFAULT_LOG_FORMAT))

    logger.handlers = [handler]
    return logger


class BaseLogger(object):
    @staticmethod
    def log(*args):
        pass


class NoOpLogger(BaseLogger):
    def __init__(self):
        self.logger = reset_logger(
            name='.'.join([__name__, self.__class__.__name__]),
            level=logging.NOTSET,
            handler=logging.NullHandler(),
        )


class SimpleLogger(BaseLogger):
    def __init__(self, min_level=enums.LogLevels.INFO):
        self.level = min_level
        self.logger = reset_logger(name='.'.join([__name__, self.__class__.__name__]), level=min_level)

    def log(self, log_level, message):
        warnings.warn('this log is deprecated', DeprecationWarning)
        self.logger.log(log_level, message)


def adapt_logger(logger):
    if isinstance(logger, logging.Logger):
        return logger

    if isinstance(logger, (SimpleLogger, NoOpLogger)):
        return logger.logger

    return logger
