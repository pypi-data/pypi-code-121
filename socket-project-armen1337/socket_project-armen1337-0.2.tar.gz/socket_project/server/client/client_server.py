from socket_project.utils import Logger
from socket_project.server.base_server import BaseServer


class Client(BaseServer):
    @BaseServer._socket_initializer
    def connect(self):
        Logger.info(f"Connected to the server '{self._host}:{self._port}' successfully")
        self._sock.connect((self._host, self._port))

    @BaseServer._requires_sock
    def send_message(self, msg: bytes | str):
        if isinstance(msg, str):
            msg = msg.encode()
        
        self._sock.sendall(msg)
