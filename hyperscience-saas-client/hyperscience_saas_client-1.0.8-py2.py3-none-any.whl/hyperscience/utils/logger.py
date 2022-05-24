"""
Global logger to be used by saas client library
"""
import logging

from .singleton import Singleton


class HyperscienceLogging(metaclass=Singleton):
    """
    HyperscienceLogging provides api for controlling log options of this library.
    """

    def __init__(self) -> None:
        super().__init__()
        logging.basicConfig(level=logging.ERROR)
        self._logger = logging.getLogger('hyperscience')

    def set_hyperscience_logging_level(self, level: str) -> None:
        """
        Setting logging level of hyperscience library.
        :param level: logging level to be used (e.g. CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG)
        :type level: str
        """
        self._logger.setLevel(level)

    def get_logger(self) -> logging.Logger:
        """
        Get logger which is used by the client library
        :return: Logger instance
        :rtype: logging.Logger
        """
        return self._logger
