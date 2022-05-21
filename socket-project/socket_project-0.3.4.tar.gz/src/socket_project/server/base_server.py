import socket

from socket_project import _config
from socket_project.utils.exceptions import ConnectionRequiredException


class BaseServer:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._sock = None
    
    def get_host(self) -> str:
        return self._host
    
    def get_port(self) -> int:
        return self._port

    def _requires_sock(func):
        """ Decorator for validating that a certain method requires self._sock variable to not be None """
        def wrapper(self, *args, **kwargs):
            if self._sock is None:
                raise ConnectionRequiredException("Connection is required! Make sure you called the appropriate method before interaction.")
            func(self, *args, **kwargs)

        return wrapper

    def _socket_initializer(func):
        """ Decorator for those methods which initialize self._sock variable before execution """
        def wrapper(self, *args, **kwargs):
            if self._sock is None:
                self._sock = socket.socket(_config.ADDRESS_FAMILY, _config.SOCKET_TYPE)
            func(self, *args, **kwargs)

        return wrapper
