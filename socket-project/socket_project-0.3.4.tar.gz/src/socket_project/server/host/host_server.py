import socket

from socket_project.http._file_handlers import FileHandler
from socket_project.utils import Logger
from socket_project.server.base_server import BaseServer
from socket_project.http.url import URLRegistrar


class Host(BaseServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = URLRegistrar()

    @BaseServer._socket_initializer
    def run_server(self) -> None:
        try:
            self._sock.bind((self._host, self._port))
            Logger.info(f"Server started at http://{self._host}:{self._port}")
        except socket.gaierror:
            Logger.exception("socket.gaierror -> Invalid host or port")
            return

        self._sock.listen()
        self._handle_client_requests()

    def _handle_client_requests(self):
        while True:
            self._conn, self._address = self._sock.accept()

            with self._conn:
                msg = self._conn.recv(50 * 1024)

                if msg.decode().lower().strip() in ["destroy", "exit", "quit", "q"]:
                    break

                self._serve_files(msg)

    def _serve_files(self, msg: bytes):
        msg_utf8 = msg.decode('utf-8').split('\r\n')
        Logger.info(msg_utf8[0])
        file_response = FileHandler._render_files(msg_utf8, self.url.get_urls())

        self._conn.sendall(file_response)
