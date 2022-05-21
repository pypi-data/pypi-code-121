import mimetypes

from socket_project import config


class FileHandler:
    def __init__(self, filepath: str):
        self._path = filepath
        with open(self._path, 'r') as f:
            self._contents = "".join(f.readlines())

    @property
    def contents(self) -> str:
        return self._contents

    @staticmethod
    def render_files(msg_utf8: list[str]) -> bytes:
        """ :param msg_utf8  msg.decode('utf-8').split('\r\n') """

        header = 'HTTP/1.1 200 OK\n'
        filename = msg_utf8[0].split(" ")[1].lstrip("/")
        filename = filename if filename != '' else 'index.html'

        try:
            with open(config.FRONTENDS_FOLDER + filename, 'rb') as f:
                response = f.read()
        except FileNotFoundError:
            with open(config.FRONTENDS_FOLDER + "404.html", 'rb') as f:
                response = f.read()

        mimetype = mimetypes.guess_type(filename)[0]
        mimetype = mimetype if mimetype is not None else 'text/html'

        header += 'Content-Type: ' + str(mimetype) + '\n\n'

        return header.encode() + response
