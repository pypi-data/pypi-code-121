"""
Log formatter.

Authors:
    Dmitry Parfyonov <parfyonov.dima@gmail.com>
"""

# import

import datetime
import logging

# LogFormatter

class LogFormatter(logging.Formatter):
    def formatTime(self, record: logging.LogRecord, datefmt: str or None = None):
        """
        Format time.
        Args:
            record:
            datefmt:
        Returns:
            str
        """
        ct = datetime.datetime.fromtimestamp(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%dT%H:%M:%S")
            s = "%s.%03d" % (t, record.msecs)

        return s
