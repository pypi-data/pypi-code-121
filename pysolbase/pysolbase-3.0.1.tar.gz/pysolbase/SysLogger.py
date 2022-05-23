"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2017 Laurent Labatut / Laurent Champagnac
#
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ===============================================================================
"""

from logging.handlers import SysLogHandler
import socket

from gevent import GreenletExit

from pysolbase.SolBase import SolBase


# noinspection PyPep8
class SysLogger(SysLogHandler):
    """
    Sys log handler (will format and emit logs toward rsyslog)
    """

    def __init__(self, address="/dev/log", facility=SysLogHandler.LOG_LOCAL1, socktype=socket.SOCK_DGRAM,
                 log_callback=None):
        """
        Init
        :param address: tuple ('ip', port) or string "target"
        :type address:  str, tuple
        :param facility: log facility
        :type facility: int
        :param socktype: Type of socket
        :type socktype: socket.SocketKind
        :param log_callback: Callback for unit test
        """

        # To avoid some warnings
        self.socket = None
        self.address = address

        # Store
        self._log_callback = log_callback
        self.socktype = socktype

        # Base call
        SysLogHandler.__init__(self, address, facility)

    def notify_log(self, msg):
        """
        Notify log to callback if set (unittest purpose)
        :param msg: Log message
        :type msg: str,bytes
        """
        # noinspection PyBroadException
        try:
            if self._log_callback:
                self._log_callback(msg)
        except:
            pass

    def emit(self, record):
        """
        Emit a record.
        :param record: The record to log
        :type record: logging.LogRecord
        """

        # Write
        # noinspection PyBroadException
        try:
            # Format
            msg = self.format(record) + '\000'

            # Get component name
            cn = SolBase.get_compo_name()

            # We append the machine+component name at the beginning
            msg = u"{0} | {1} | {2}".format(SolBase.get_machine_name(), cn, msg)
            msg = msg.encode('utf-8')

            # Add priority + facility (int)
            priority = '<%d>' % self.encodePriority(self.facility, self.mapPriority(record.levelname))
            priority = priority.encode('utf-8')

            # Cn
            cn = cn.encode('utf-8')

            # noinspection PyAugmentAssignment
            msg = priority + cn + b": " + msg

            # Notify
            self.notify_log(msg)

            # Send to socket
            if self.unixsocket:
                try:
                    self.socket.send(msg)
                except socket.error:
                    # noinspection PyUnresolvedReferences
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            elif self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            else:
                self.socket.sendall(msg)
        except GreenletExit:
            pass
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
