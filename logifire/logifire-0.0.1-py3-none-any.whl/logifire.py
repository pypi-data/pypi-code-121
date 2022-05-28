"""
Logifire.

Authors:
    Dmitry Parfyonov <parfyonov.dima@gmail.com>
"""

# import

import logging
from typing import List

from .logformatter import LogFormatter
from .blowout import Blowout, BlowoutProcess
from .logbranch import Logbranch

# Logifire

class Logifire(object):

    DEFAULT_FORMAT = '%(asctime)s %(process)-7d [%(levelname)-8s] %(name)s.%(funcName)s: %(message)s'

    def __init__(self,
                 name: str = 'main',
                 level: int = logging.DEBUG,
                 branches: List[Logbranch] or None = None,
                 formatter: logging.Formatter or str or None = None,
                 blowout: Blowout or None = None
                 ):
        """
        Init.
        Args:
            name: service/application name
            level: logger level
            branches: list of Logbranch objects, stderr handler by default, pass empty list to set no handlers
            formatter: log formatter or log format
            blowout: blowout source for mute message (BlowoutProcess by default)
        """
        self._name = name
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(level)

        if not formatter or isinstance(formatter, str):
            self._formatter = LogFormatter(fmt=formatter or self.DEFAULT_FORMAT)
        else:
            self._formatter = formatter

        self._blowout = blowout or BlowoutProcess()

        if branches is None:  # set stderr handler by default
            self.add(Logbranch(logging.StreamHandler()))
        else:
            self.add_many(branches)

    def add_many(self, branches: List[Logbranch]):
        """
        Add log branches.
        Args:
            branches: list of Logbranch objects
        """
        for lp in branches:
            self.add(lp)

    def add(self, logbranch: Logbranch):
        """
        Add Logbranch.
        Args:
            logbranch:
        """
        logbranch.set_logifire(self)
        self._logger.addHandler(logbranch.get_handler())

    def get_formatter(self) -> logging.Formatter:
        """
        Get log formatter.
        """
        return self._formatter

    def get_blowout(self) -> Blowout:
        """
        Get blowout source.
        """
        return self._blowout

    def set_level(self, level: int):
        """
        Set global log level.
        Args:
            level:
        """
        self._logger.setLevel(level)

    def set_name(self, name: str):
        """
        Set logger name.
        Args:
            name:
        """
        new_logger = logging.getLogger(name)
        new_logger.setLevel(self._logger.level)
        new_logger.handlers = list(self._logger.handlers)

        self._logger.handlers = []
        self._logger = new_logger

    def debug(self, msg: str, *args, _exc_info=None, _extra=None, _stack_info=False, _stacklevel=1, **kwargs):
        """
        Log debug message.
        """
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                msg=msg.format(*args, **kwargs),
                exc_info=_exc_info,
                extra=_extra,
                stack_info=_stack_info,
                stacklevel=_stacklevel + 1
            )

    def info(self, msg: str, *args, _exc_info=None, _extra=None, _stack_info=False, _stacklevel=1, **kwargs):
        """
        Log info message.
        """
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info(
                msg=msg.format(*args, **kwargs),
                exc_info=_exc_info,
                extra=_extra,
                stack_info=_stack_info,
                stacklevel=_stacklevel + 1
            )

    def warning(self, msg: str, *args, _exc_info=None, _extra=None, _stack_info=False, _stacklevel=1, **kwargs):
        """
        Log warning message.
        """
        if self._logger.isEnabledFor(logging.WARNING):
            self._logger.warning(
                msg=msg.format(*args, **kwargs),
                exc_info=_exc_info,
                extra=_extra,
                stack_info=_stack_info,
                stacklevel=_stacklevel + 1
            )

    def error(self, msg: str, *args, _exc_info=None, _extra=None, _stack_info=False, _stacklevel=1, **kwargs):
        """
        Log error message.
        """
        if self._logger.isEnabledFor(logging.ERROR):
            self._logger.error(
                msg=msg.format(*args, **kwargs),
                exc_info=_exc_info,
                extra=_extra,
                stack_info=_stack_info,
                stacklevel=_stacklevel + 1
            )

    def exception(self, msg: str, *args, _exc_info=True, _extra=None, _stack_info=False, _stacklevel=1, **kwargs):
        """
        Log error message with an exception information.
        """
        self.error(
            msg, *args, _exc_info=_exc_info, _extra=_extra, _stack_info=_stack_info, _stacklevel=_stacklevel, **kwargs
        )

    def critical(self, msg: str, *args, _exc_info=None, _extra=None, _stack_info=False, _stacklevel=1, **kwargs):
        """
        Log critical message.
        """
        if self._logger.isEnabledFor(logging.CRITICAL):
            self._logger.critical(
                msg=msg.format(*args, **kwargs),
                exc_info=_exc_info,
                extra=_extra,
                stack_info=_stack_info,
                stacklevel=_stacklevel + 1
            )

    fatal = critical

    def log(self, level: int, msg: str, *args, _exc_info=None, _extra=None, _stack_info=False, _stacklevel=1, **kwargs):
        """
        Log message.
        """
        if self._logger.isEnabledFor(level):
            self._logger.log(
                level=level,
                msg=msg.format(*args, **kwargs),
                exc_info=_exc_info,
                extra=_extra,
                stack_info=_stack_info,
                stacklevel=_stacklevel + 1
            )
