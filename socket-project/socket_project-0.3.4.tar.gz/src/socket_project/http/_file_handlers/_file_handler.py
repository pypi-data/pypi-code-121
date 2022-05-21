import mimetypes
import os

from socket_project import _config
from socket_project.utils import Logger


class FileHandler:
    def __init__(self, filepath: str):
        self._path = filepath
        with open(self._path, 'r') as f:
            self._contents = "".join(f.readlines())

    @property
    def contents(self) -> str:
        return self._contents

    @staticmethod
    def _render_files(msg_utf8: list[str], urls: dict) -> bytes:
        """
        :param msg_utf8: msg.decode('utf-8').split('\r\n')
        :param urls: URLRegistrar().get_urls()
        """

        header = 'HTTP/1.1 200 OK\n'

        try:
            resource = msg_utf8[0].split(" ")[1]
            filename = resource.lstrip("/")
        except IndexError:
            Logger.exception(msg_utf8)
            raise IndexError("CUSTOM INDEX ERROR FOR DEBUGGING")

        for url, get_filepath in urls.items():
            if url == resource and os.path.exists(_config.FRONTENDS_FOLDER + get_filepath()):
                filename = get_filepath()

        try:
            with open(_config.FRONTENDS_FOLDER + filename, 'rb') as f:
                response = f.read()
        except FileNotFoundError:
            with open(_config.HTML404, 'rb') as f:
                response = f.read()
                header = header.replace("200", "404")

        mimetype = mimetypes.guess_type(filename)[0]
        mimetype = mimetype if mimetype is not None else 'text/html'

        header += 'Content-Type: ' + str(mimetype) + '\n\n'

        return header.encode() + response


def render():
    pass
