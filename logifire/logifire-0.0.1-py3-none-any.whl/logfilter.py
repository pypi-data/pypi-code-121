"""
Log filter.

Authors:
    Dmitry Parfyonov <parfyonov.dima@gmail.com>
"""

# import

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logbranch import Logbranch

# Logfilter

class Logfilter(logging.Filter):
    def __init__(self, logbranch: 'Logbranch'):
        """
        Init.
        Args:
            logbranch:
        """
        super(Logfilter, self).__init__()

        self._logbranch = logbranch

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter.
        Args:
            record: log message
        """
        return self._logbranch.get_blowout().can_emit(
            handler_id=self._logbranch.get_handler_id(),
            blowout_seconds=self._logbranch.get_blowout_seconds()
        )
