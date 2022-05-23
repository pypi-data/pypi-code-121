# ----------------------------------------------------------------------------
# Description    : Transport layer (abstract, IP, file, dummy)
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import socket
import os
import sys

from qblox_instruments.ieee488_2 import Transport


# -- class -------------------------------------------------------------------

class IpTransport(Transport):
    """
    Class for data transport of IP socket.
    """

    # ------------------------------------------------------------------------
    def __init__(
        self,
        host: str,
        port: int = 5025,
        timeout: float = 60.0,
        snd_buf_size: int = 512 * 1024,
    ):
        """
        Create IP socket transport class.

        Parameters
        ----------
        host : str
            Instrument IP address.
        port : int
            Instrument port.
        timeout : float
            Instrument call timeout in seconds.
        snd_buf_size : int
            Instrument buffer size for transmissions to instrument.

        Returns
        ----------

        Raises
        ----------
        """

        # 1. Setup timeout (before connecting)
        # 2. Enlarge buffer
        # 3. Send immediately
        # 4. Setup keep alive pinging
        # 5. Connect
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(3)
        self._socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_SNDBUF,
            snd_buf_size
        )
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._set_keepalive()
        self._socket.connect((host, port))

        # Timeout after connecting
        self._socket.settimeout(timeout)

    # ------------------------------------------------------------------------
    def _set_keepalive(
        self,
        after_idle_sec: int=60,
        interval_sec: int=60,
        max_fails: int=5
    ) -> None:
        """
        This function instructs the TCP socket to send a heart beat every n
        seconds to detect dead connections. It's the TCP equivalent of the
        IRC ping-pong protocol and allows for better cleanup / detection
        of dead TCP connections.
        It activates after 60 second (after_idle_sec) of idleness, then sends
        a keepalive ping once every 60 seconds (interval_sec), and closes the
        connection after 5 failed ping (max_fails), or 300 seconds by default.

        Parameters
        ----------
        after_idle_sec : int
            Activate keepalive after n seconds.
        interval_sec : int
            Packet interval in seconds.
        max_fails : int
            Maximum number of failed packets.

        Returns
        ----------

        Raises
        ----------
        """

        if os.name == "nt":  # Windows
            after_idle_sec *= 1000
            interval_sec *= 1000
            # pylint: disable=no-member
            self._socket.ioctl(
                socket.SIO_KEEPALIVE_VALS,
                (1, after_idle_sec, interval_sec)
            )
        elif sys.platform == "darwin":  # MacOS
            TCP_KEEPALIVE = 0x10  # From /usr/include, not exported by Python's socket module
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self._socket.setsockopt(
                socket.IPPROTO_TCP,
                TCP_KEEPALIVE,
                interval_sec
            )
        else:  # Linux
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self._socket.setsockopt(
                socket.IPPROTO_TCP,
                socket.TCP_KEEPIDLE,
                after_idle_sec
            )
            self._socket.setsockopt(
                socket.IPPROTO_TCP,
                socket.TCP_KEEPINTVL,
                interval_sec
            )
            self._socket.setsockopt(
                socket.IPPROTO_TCP,
                socket.TCP_KEEPCNT,
                max_fails
            )

    # ------------------------------------------------------------------------
    def __del__(self) -> None:
        """
        Delete IP socket transport class.

        Parameters
        ----------

        Returns
        ----------

        Raises
        ----------
        """

        self.close()

    # ------------------------------------------------------------------------
    def close(self) -> None:
        """
        Close IP socket.

        Parameters
        ----------

        Returns
        ----------

        Raises
        ----------
        """

        self._socket.close()

    # ------------------------------------------------------------------------
    def write(self, cmd_str: str) -> None:
        """
        Write command to instrument over IP socket.

        Parameters
        ----------
        cmd_str : str
            Command

        Returns
        ----------

        Raises
        ----------
        """

        out_str = cmd_str + "\n"
        self.write_binary(out_str.encode("ascii"))

    # ------------------------------------------------------------------------
    def write_binary(self, data: bytes) -> None:
        """
        Write binary data to instrument over IP socket.

        Parameters
        ----------
        data : bytes
            Binary data

        Returns
        ----------

        Raises
        ----------
        """

        exp_len = len(data)
        act_len = 0
        while True:
            act_len += self._socket.send(data[act_len:exp_len])
            if act_len == exp_len:
                break

    # ------------------------------------------------------------------------
    def read_binary(self, size: int) -> bytes:
        """
        Read binary data from instrument over IP socket.

        Parameters
        ----------
        size : int
            Number of bytes

        Returns
        ----------
        bytes
            Binary data array of length "size".

        Raises
        ----------
        """

        data = self._socket.recv(size)
        act_len = len(data)
        exp_len = size
        while act_len != exp_len:
            data += self._socket.recv(exp_len - act_len)
            act_len = len(data)
        return data

    # ------------------------------------------------------------------------
    def readline(self) -> str:
        """
        Read data from instrument over IP socket.

        Parameters
        ----------

        Returns
        ----------
        str
            String with data.

        Raises
        ----------
        """

        return self._socket.makefile().readline()
