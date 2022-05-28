"""
SysLog handler.

Authors:
    Dmitry Parfyonov <parfyonov.dima@gmail.com>
"""

# import

import sys
from logging.handlers import SysLogHandler

# SysLogifireHandler

class SysLogifireHandler(SysLogHandler):

    def __init__(self, address=None, facility=None, socktype=None):
        """
        Init.
        Args:
            address (str or tuple[str, int]):
            facility (int):
            socktype (int):
        """
        kwargs = {}

        if address is None:
            if sys.platform.startswith('linux'):  # Linux
                address = '/dev/log'
            elif sys.platform.startswith('darwin'):  # Mac OS X
                address = '/var/run/syslog'
            else:  # Windows
                address = ('localhost', 514)

        kwargs['address'] = address

        if facility is not None:
            kwargs['facility'] = facility

        if socktype is not None:
            kwargs['socktype'] = socktype

        super(SysLogifireHandler, self).__init__(**kwargs)

    def format(self, record):
        """
        Format the specified record.

        If a formatter is set, use it. Otherwise, use the default formatter
        for the module.

        Args:
            record (logging.LogRecord):
        """
        msg = super(SysLogifireHandler, self).format(record)

        return msg.replace("\r\n", '|_|').replace("\n", '|_|')
