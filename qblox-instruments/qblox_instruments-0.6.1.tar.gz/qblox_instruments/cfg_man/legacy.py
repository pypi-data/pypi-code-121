# ----------------------------------------------------------------------------
# Description    : Helper functions for updating using a legacy configuration
#                  manager
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import struct
import socket
from typing import BinaryIO, Tuple


# -- definitions -------------------------------------------------------------

# Transfer size from file to socket and vice versa for file transfers.
_BUF_SIZE = 4096


# -- functions ---------------------------------------------------------------

def send_msg(sock: socket.socket, message: bytes) -> None:
    """
    Sends a bytestring to the socket, encapsulated in the legacy protocol
    message format.

    Parameters
    ----------
    sock: socket
        The socket to send to.
    message: bytes
        The message to send.

    Returns
    -------

    Raises
    ------
    TimeoutError
        If we failed to send the expected amount of bytes within the socket
        timeout.
    OSError
        If we failed to send the expected amount of bytes at all.
    """
    sock.sendall(struct.pack("I", len(message)) + message)


# ----------------------------------------------------------------------------
def send_msg_file(sock: socket.socket, file: BinaryIO) -> None:
    """
    Sends a seekable file to the socket, encapsulated in the legacy protocol
    message format.

    Parameters
    ----------
    sock: socket
        The socket to send to.
    file: BinaryIO
        Seekable and readable file descriptor to read from and send as a
        whole.

    Returns
    -------

    Raises
    ------
    TimeoutError
        If we failed to send the expected amount of bytes within the socket
        timeout.
    OSError
        If we failed to send the expected amount of bytes at all.
    """
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    sock.sendall(struct.pack("I", size))
    while size:
        if size > _BUF_SIZE:
            buf_size = _BUF_SIZE
        else:
            buf_size = size
        data = file.read(buf_size)
        sock.sendall(data)
        size -= len(data)


# ----------------------------------------------------------------------------
def send_version(sock: socket.socket, version: Tuple[int, int, int]) -> None:
    """
    Sends the given client version to the socket as part of the connection
    handshake.

    Parameters
    ----------
    sock: socket
        The socket to send to.
    version: Tuple[int, int, int]
        Our client version.

    Returns
    -------

    Raises
    ------
    TimeoutError
        If we failed to send the expected amount of bytes within the socket
        timeout.
    OSError
        If we failed to send the expected amount of bytes at all.
    """
    send_msg(sock, bytes(version))


# ----------------------------------------------------------------------------
def recv_all(sock: socket.socket, count: int) -> bytes:
    """
    Receives exactly the given amount of bytes. The socket timeout resets
    every time we receive at least one byte.

    Parameters
    ----------
    sock: socket
        The socket to receive from.
    count: int
        The number of bytes to wait for.

    Returns
    -------
    bytes
        The received message.

    Raises
    ------
    TimeoutError
        If we failed to get even a single additional byte within the socket
        timeout.
    OSError
        If a socket exception occurs.
    RuntimeError
        If the remote end closed the connection prematurely.
    """
    parts = []
    remain = count
    while remain > 0:
        buf = sock.recv(remain)
        if len(buf) == 0:
            raise RuntimeError("Remote closed connection unexpectedly")
        parts.append(buf)
        remain -= len(buf)
    return b"".join(parts)


# ----------------------------------------------------------------------------
def recv_msg(sock: socket.socket) -> bytes:
    """
    Receives a bytestring from the socket, encapsulated in the legacy
    protocol message format.

    Parameters
    ----------
    sock: socket
        The socket to receive from.

    Returns
    -------
    bytes
        The received message.

    Raises
    ------
    TimeoutError
        If we failed to send the expected amount of bytes within the socket
        timeout.
    OSError
        If we failed to send the expected amount of bytes at all.
    """
    size = struct.unpack("I", recv_all(sock, 4))[0]
    return recv_all(sock, size)


# ----------------------------------------------------------------------------
def recv_file(sock: socket.socket, file: BinaryIO) -> None:
    """
    Receives a bytestring from the socket, encapsulated in the legacy
    protocol message format, and streams it to a file.

    Parameters
    ----------
    sock: socket
        The socket to receive from.
    file: BinaryIO
        The file to write to.

    Returns
    -------
    None

    Raises
    ------
    TimeoutError
        If we failed to send the expected amount of bytes within the socket
        timeout.
    OSError
        If we failed to send the expected amount of bytes at all.
    """
    size = struct.unpack("I", recv_all(sock, 4))[0]
    while size:
        if size > _BUF_SIZE:
            buf_size = _BUF_SIZE
        else:
            buf_size = size
        data = sock.recv(buf_size)
        file.write(data)
        size -= len(data)


# ----------------------------------------------------------------------------
def recv_version(sock: socket.socket) -> Tuple[int, int, int]:
    """
    Receives the server version from the socket as part of the connection
    handshake.

    Parameters
    ----------
    sock: socket
        The socket to receive from.

    Returns
    -------
    Tuple[int, int, int]
        The server version.

    Raises
    ------
    TimeoutError
        If we failed to send the expected amount of bytes within the socket
        timeout.
    OSError
        If we failed to send the expected amount of bytes at all.
    """
    return tuple(recv_msg(sock))


# ----------------------------------------------------------------------------
def recv_ack(sock: socket.socket) -> None:
    """
    Receives an ack/nack from the socket, throwing an exception if nack.

    Parameters
    ----------
    sock: socket
        The socket to receive from.

    Returns
    -------

    Raises
    ------
    TimeoutError
        If we failed to send the expected amount of bytes within the socket
        timeout.
    OSError
        If we failed to send the expected amount of bytes at all.
    RuntimeError
        If the remote end closed the connection prematurely, or if we received
        a nack.
    """
    ack_nack = recv_msg(sock)
    if ack_nack not in (b"ack", b"nack"):
        raise RuntimeError(
            "Protocol error: expected ack or nack, but got {}".format(ack_nack)
        )
    message = recv_msg(sock)
    if ack_nack == b"nack":
        raise RuntimeError(
            message.decode(encoding="ascii", errors="replace")
        )


# ----------------------------------------------------------------------------
def exchange_version(
    sock: socket.socket,
    version: Tuple[int, int, int]
) -> Tuple[int, int, int]:
    """
    Handles the version exchange handshake at the start of a legacy connection
    for the given socket.

    Parameters
    ----------
    sock: socket
        The socket to receive from.
    version: Tuple[int, int, int]
        Our client version.

    Returns
    -------
    Tuple[int, int, int]
        The server version.

    Raises
    ------
    TimeoutError
        If a timeout occurs during the handshake.
    OSError
        If we failed to send or receive due to an operating system error.
    """
    send_version(sock, version)
    return recv_version(sock)
