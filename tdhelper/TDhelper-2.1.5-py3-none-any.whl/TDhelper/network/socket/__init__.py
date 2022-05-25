import socket
from TDhelper.network.socket.model.SOCKET_MODELS import SOCKET_TYPE, SOCKET_EVENT
from TDhelper.Event.Event import *

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
class base(Event):
    def __init__(self):
        self._mysocket = None
        self._socket_type = SOCKET_TYPE.TCPIP
        super(base, self).__init__()

    def createsocket(self, sType=SOCKET_TYPE.TCPIP, customize_socket:socket.socket= None):
        self._socket_type = sType
        if not customize_socket:
            if self._socket_type == SOCKET_TYPE.TCPIP:
                self._mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif self._socket_type == SOCKET_TYPE.UDP:
                self._mysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self._mysocket= customize_socket

    def setTimeout(self, timeout):
        self._mysocket.settimeout(timeout)

    def bind(self, uri):
        if self._mysocket:
            self._mysocket.bind(uri)

    def listen(self, count):
        if self._mysocket:
            self._mysocket.listen(count)

    def accept(self):
        return self._mysocket.accept()

    def recv(self, connect=None, recvLen=100):
        if self._socket_type == SOCKET_TYPE.TCPIP:
            return connect.recv(recvLen),connect
        else:
            return self._mysocket.recvfrom(recvLen)

    def send(self, connect, buff):
        if self._socket_type == SOCKET_TYPE.TCPIP:
            connect.send(buff)
        else:
            self._mysocket.sendto(buff, connect)

    def connection(self, uri):
        try:
            self._mysocket.connect(uri)
        except Exception as e:
            raise e

    def getSocket(self):
        return self._mysocket

    def close(self):
        self._mysocket.shutdown(socket.SHUT_RDWR)
        self._mysocket.close()
