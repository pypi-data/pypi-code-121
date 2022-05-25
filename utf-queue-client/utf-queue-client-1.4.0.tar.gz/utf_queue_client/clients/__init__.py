import logging
from contextlib import contextmanager
from typing import Union
from logging import DEBUG, INFO, WARNING, CRITICAL


__all__ = ["configure_logger", "get_logger", "Loggable", "classproperty"]


class classproperty(property):
    """Helper class for defining a class method as a property"""

    def __get__(self, cls, owner):  # noqa
        return classmethod(self.fget).__get__(None, owner)()


class Loggable:
    LOG_DEBUG = DEBUG
    LOG_INFO = INFO
    LOG_WARNING = WARNING
    LOG_CRITICAL = CRITICAL

    @classproperty
    def logger(cls) -> logging.Logger:  # noqa
        """Returns a logger specific to the derived class' name"""
        return get_logger(cls.__name__)

    @contextmanager
    def set_log_level(self, level: Union[int, str]):
        old_level = self.logger.level
        try:
            self.logger.setLevel(level)
            yield
        finally:
            self.logger.setLevel(old_level)


def configure_logger():
    logging.basicConfig(
        format="%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m-%d-%Y %H:%M:%S",
        level=logging.INFO,
    )


def get_logger(name: str = None) -> logging.Logger:
    configure_logger()
    return logging.getLogger(name)
