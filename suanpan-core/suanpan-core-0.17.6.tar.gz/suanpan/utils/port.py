# coding=utf-8
from __future__ import absolute_import, print_function

import sys
import ctypes
import socket
import struct
import random
import gevent
import requests
from suanpan import g
from suanpan.log import logger


def _get_open_ports():
    """
        This function will return a list of ports (TCP/UDP) that the current
        machine is listening on. It's basically a replacement for parsing
        netstat output but also serves as a good example for using the
        IP Helper API:
        https://docs.microsoft.com/en-us/windows/win32/api/iphlpapi/nf-iphlpapi-gettcptable
     """
    if sys.platform != "win32":
        raise Exception("only support win32")

    port_list = []

    DWORD = ctypes.c_ulong
    NO_ERROR = 0
    NULL = ""
    bOrder = 0

    # define some MIB constants used to identify the state of a TCP port
    MIB_TCP_STATE_CLOSED = 1
    MIB_TCP_STATE_LISTEN = 2
    MIB_TCP_STATE_SYN_SENT = 3
    MIB_TCP_STATE_SYN_RCVD = 4
    MIB_TCP_STATE_ESTAB = 5
    MIB_TCP_STATE_FIN_WAIT1 = 6
    MIB_TCP_STATE_FIN_WAIT2 = 7
    MIB_TCP_STATE_CLOSE_WAIT = 8
    MIB_TCP_STATE_CLOSING = 9
    MIB_TCP_STATE_LAST_ACK = 10
    MIB_TCP_STATE_TIME_WAIT = 11
    MIB_TCP_STATE_DELETE_TCB = 12

    ANY_SIZE = 1

    # defing our MIB row structures
    class MIB_TCPROW(ctypes.Structure):
        _fields_ = [('dwState', DWORD),
                    ('dwLocalAddr', DWORD),
                    ('dwLocalPort', DWORD),
                    ('dwRemoteAddr', DWORD),
                    ('dwRemotePort', DWORD)]

    class MIB_UDPROW(ctypes.Structure):
        _fields_ = [('dwLocalAddr', DWORD),
                    ('dwLocalPort', DWORD)]

    dwSize = DWORD(0)

    # call once to get dwSize
    ctypes.windll.iphlpapi.GetTcpTable(NULL, ctypes.byref(dwSize), bOrder)

    # ANY_SIZE is used out of convention (to be like MS docs); even setting this
    # to dwSize will likely be much larger than actually necessary but much
    # more efficient that just declaring ANY_SIZE = 65500.
    # (in C we would use malloc to allocate memory for the *table pointer and
    #  then have ANY_SIZE set to 1 in the structure definition)

    ANY_SIZE = dwSize.value

    class MIB_TCPTABLE(ctypes.Structure):
        _fields_ = [('dwNumEntries', DWORD),
                    ('table', MIB_TCPROW * ANY_SIZE)]

    tcpTable = MIB_TCPTABLE()
    tcpTable.dwNumEntries = 0  # define as 0 for our loops sake

    # now make the call to GetTcpTable to get the data
    if (ctypes.windll.iphlpapi.GetTcpTable(ctypes.byref(tcpTable),
                                           ctypes.byref(dwSize), bOrder) == NO_ERROR):

        maxNum = tcpTable.dwNumEntries
        placeHolder = 0

        # loop through every connection
        while placeHolder < maxNum:

            item = tcpTable.table[placeHolder]
            placeHolder += 1

            # format the data we need (there is more data if it is useful -
            #    see structure definition)
            lPort = item.dwLocalPort
            lPort = socket.ntohs(lPort)
            lAddr = item.dwLocalAddr
            lAddr = socket.inet_ntoa(struct.pack('L', lAddr))
            portState = item.dwState

            # only record TCP ports where we're listening on our external
            #    (or all) connections
            if str(lAddr) != "127.0.0.1" and portState == MIB_TCP_STATE_LISTEN:
                port_list.append({"port": lPort, "type": "TCP"})

    else:
        print("Error occurred when trying to get TCP Table")

    dwSize = DWORD(0)

    # call once to get dwSize
    ctypes.windll.iphlpapi.GetUdpTable(NULL, ctypes.byref(dwSize), bOrder)

    ANY_SIZE = dwSize.value  # again, used out of convention

    #                            (see notes in TCP section)

    class MIB_UDPTABLE(ctypes.Structure):
        _fields_ = [('dwNumEntries', DWORD),
                    ('table', MIB_UDPROW * ANY_SIZE)]

    udpTable = MIB_UDPTABLE()
    udpTable.dwNumEntries = 0  # define as 0 for our loops sake

    # now make the call to GetUdpTable to get the data
    if (ctypes.windll.iphlpapi.GetUdpTable(ctypes.byref(udpTable),
                                           ctypes.byref(dwSize), bOrder) == NO_ERROR):

        maxNum = udpTable.dwNumEntries
        placeHolder = 0
        while placeHolder < maxNum:

            item = udpTable.table[placeHolder]
            placeHolder += 1
            lPort = item.dwLocalPort

            lPort = socket.ntohs(lPort)
            lAddr = item.dwLocalAddr

            lAddr = socket.inet_ntoa(struct.pack('L', lAddr))

            # only record UDP ports where we're listening on our external
            #    (or all) connections
            if str(lAddr) != "127.0.0.1":
                port_list.append({"port": lPort, "type": "UDP"})
    else:
        print("Error occurred when trying to get UDP Table")

    return port_list


class PortHelper(object):
    def __init__(self, port_min, port_max):
        self.port_min = port_min
        self.port_max = port_max

    def get_free_port(self):
        op = set(range(self.port_min, self.port_max))
        open_ports = _get_open_ports()
        for port in open_ports:
            if self.port_min <= port['port'] <= self.port_max:
                op.discard(port['port'])

        if not op:
            raise Exception("not enough free port")

        return random.sample(op, 1)[0]


helper = PortHelper(g.portStart, g.portEnd)


def need_free_port():
    if g.currentOS == "windows":
        return True

    return False


def get_free_port():
    if need_free_port():
        return helper.get_free_port()

    raise Exception("not required for non-Windows systems")


def register_server(node_port, real_port):
    if not need_free_port():
        return

    protocol = "https" if g.hostTls else "http"
    url = f"{protocol}://localhost:{g.backendPort}/app/service/register"
    param = {"appId": g.appId, "nodeId": g.nodeId, "userId": g.userId, "nodePort": node_port, "port": real_port}

    while True:
        try:
            res = requests.post(url, json=param)
            res.raise_for_status()
            ret = res.json()
            if not ret["success"]:
                raise Exception(ret["msg"])

            return
        except Exception as e:
            logger.warn(f"register server: {e}")
            gevent.sleep(10)

# if __name__ == "__main__":
#     helper = PortHelper(5000, 6000)
#     p = helper.get_free_port()
#     print(p)
