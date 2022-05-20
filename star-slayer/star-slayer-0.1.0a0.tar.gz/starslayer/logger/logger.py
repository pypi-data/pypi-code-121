"""
Logger Module. It cointains the GameLogger class,
from which is created the objects that logs events
of the program.
"""

from logging import INFO, FileHandler, Formatter, StreamHandler, getLogger
from typing import TYPE_CHECKING

from ..auxiliar import Singleton
from ..consts import LOG_PATH

if TYPE_CHECKING:

    from logging import Logger


class GameLogger(metaclass=Singleton):
    """
    Class that registers game events.
    Made with singleton pattern.
    """

    def __init__(self,
                 *,
                 log_name: str="TheStarThatSlays",
                 log_level: int=INFO,
                 fmt: str="[ %(asctime)s ] [ %(levelname)s ] %(message)s",
                 date_fmt: str="%d-%m-%Y %I:%M:%S %p") -> None:
        """
        Creates an instance of 'GameLogger'.
        """

        super().__init__()

        self._format: str = fmt
        self._date_fmt: str = date_fmt

        self._formatter = Formatter(fmt=self.format, datefmt=self.date_fmt)

        self.file_handler = FileHandler(filename=LOG_PATH, encoding="utf-8")
        self.console_handler = StreamHandler()
        self.update_formatter()

        self.logger: "Logger" = getLogger(log_name)
        self.logger.setLevel(log_level)
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)


    def update_formatter(self) -> None:
        """
        Sets the formatter for every handler that the logger has.
        """

        self.file_handler.setFormatter(self.formatter)
        self.console_handler.setFormatter(self.formatter)


    @property
    def formatter(self) -> Formatter:
        """
        Returns the formatter used.
        """

        return self._formatter

    @formatter.setter
    def formatter(self, new_formatter: Formatter) -> None:
        """
        Updates automatically the formatter for every handler.
        """

        self._formatter = new_formatter
        self.update_formatter()


    @property
    def format(self) -> str:
        """
        Returns the format of the log messages.
        """

        return self._format


    @format.setter
    def format(self, new_format) -> None:

        self._format = new_format
        self.formatter = Formatter(fmt=self.format, datefmt=self.date_fmt)


    @property
    def date_fmt(self) -> str:
        """
        Returns the date format of the log messages.
        """

        return self._date_fmt


    @date_fmt.setter
    def date_fmt(self, new_date_fmt: str) -> None:

        self._date_fmt = new_date_fmt
        self.formatter = Formatter(fmt=self.format, datefmt=self.date_fmt)


    def debug(self, message: str, *args, **kwargs) -> None:
        """
        Registers an event of level DEBUG.
        """

        self.logger.debug(message, *args, **kwargs)


    def info(self, message: str, *args, **kwargs) -> None:
        """
        Registers an event of level INFO.
        """

        self.logger.info(message, *args, **kwargs)


    def warning(self, message: str, *args, **kwargs) -> None:
        """
        Registers an event of level WARNING.
        """

        self.logger.warning(message, *args, **kwargs)


    def error(self, message: str, *args, **kwargs) -> None:
        """
        Registers an event of level ERROR.
        """

        self.logger.error(message, *args, **kwargs)


    def critical(self, message: str, *args, **kwargs) -> None:
        """
        Registers an event of level CRITICAL.
        """

        self.logger.critical(message, *args, **kwargs)


    def exception(self, msg, *args, exc_info=True, **kwargs) -> None:
        """
        Registers an exception.
        """

        self.logger.exception(msg, *args, exc_info, **kwargs)
