"""
Overlay for logging.Handler.

Authors:
    Dmitry Parfyonov <parfyonov.dima@gmail.com>
"""

# import

import logging
from hashlib import md5
from typing import TYPE_CHECKING

from .logfilter import Logfilter

if TYPE_CHECKING:
    from .logifire import Logifire
    from .blowout import Blowout

# Logbranch

class Logbranch(object):
    def __init__(self,
                 handler: logging.Handler,
                 level: int = logging.NOTSET,
                 blowout_seconds: float = 0,
                 filters: list or None = None
                 ):
        """
        Init.
        Args:
            handler: log handler
            level: log handler level
            blowout_seconds: mute logs period
            filters: advanced log filters
        """
        self.__logifire = None
        self.__handler = handler
        self._filters = filters
        self._blowout_seconds = blowout_seconds

        if level != logging.NOTSET:
            self.__handler.setLevel(level)

        self.__handler_id = md5(str(self.__handler).encode('utf-8') + str(blowout_seconds).encode('utf-8')).hexdigest()

    def set_logifire(self, logifire: 'Logifire'):
        """
        Set logifire object.
        Args:
            logifire:
        """
        self.__logifire = logifire
        self.__handler.setFormatter(self.__logifire.get_formatter())

        if self._blowout_seconds > 0:
            self.__handler.addFilter(Logfilter(self))

        if self._filters:
            for f in self._filters:
                self.__handler.addFilter(f)

    def get_handler(self) -> logging.Handler:
        """
        Get handler.
        """
        assert self.__logifire is not None

        return self.__handler

    def get_handler_id(self) -> str:
        """
        Get handler id.
        """
        return self.__handler_id

    def get_blowout(self) -> 'Blowout':
        """
        Get blowout.
        """
        return self.__logifire.get_blowout()

    def get_blowout_seconds(self) -> float:
        """
        Get mute seconds.
        """
        return self._blowout_seconds
