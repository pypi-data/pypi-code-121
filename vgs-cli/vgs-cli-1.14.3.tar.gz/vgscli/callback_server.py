from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse

from vgscli.keyring_token_util import KeyringTokenUtil
from vgscli.token_handler import CodeHandler

token_util = KeyringTokenUtil()
token_handler = CodeHandler()


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith('/callback'):
            params = parse.parse_qs(self.path.split("?")[1])
            token = params['code'][0]
            token_handler.put_code(token)
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Go back to terminal".encode('utf-8'))
        return

    def log_message(self, format, *args):
        return


class RequestServer:

    server = None
    host = 'localhost'
    port = 8080

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def run(self):
        self.server = HTTPServer((self.host, self.port), RequestHandler)
        self.server.serve_forever()

    def close(self):
        self.server.server_close()
