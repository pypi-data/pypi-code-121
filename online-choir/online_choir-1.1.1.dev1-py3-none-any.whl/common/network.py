# Code borrowed from sockio, https://github.com/tiagocoutinho/sockio
import asyncio
import socket

from .log import logger

IPTOS_NORMAL = 0x0
IPTOS_LOWDELAY = 0x10
IPTOS_THROUGHPUT = 0x08
IPTOS_RELIABILITY = 0x04
IPTOS_MINCOST = 0x02


def set_socket_settings(writer: asyncio.StreamWriter, no_delay=True, tos=IPTOS_LOWDELAY, keep_alive=None):
    sock = writer.transport.get_extra_info("socket")
    try:
        if hasattr(socket, "TCP_NODELAY") and no_delay:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if hasattr(socket, "IP_TOS"):
            sock.setsockopt(socket.SOL_IP, socket.IP_TOS, tos)
        if keep_alive is not None and hasattr(socket, "SO_KEEPALIVE"):
            if isinstance(keep_alive, (int, bool)):
                keep_alive = 1 if keep_alive in {1, True} else False
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, keep_alive)
            else:
                active = keep_alive.get('active')
                idle = keep_alive.get('idle')  # aka keepalive_time
                interval = keep_alive.get('interval')  # aka keepalive_intvl
                retry = keep_alive.get('retry')  # aka keepalive_probes
                if active is not None:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, active)
                if idle is not None:
                    sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, idle)
                if interval is not None:
                    sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, interval)
                if retry is not None:
                    sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, retry)
    except OSError as e:
        logger.warning(f"Failed to set the socket options ({e})")
