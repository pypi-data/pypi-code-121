from thompcoutils.log_utils import get_logger
import urllib.request
import json
import ssl
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from werkzeug.exceptions import BadRequestKeyError


class MissingArgumentException(Exception):
    pass


class Server:
    @staticmethod
    def get_info(args, request):
        if args is None:
            args = []
        values = {}
        for arg in args:
            found = False
            if request.json is not None:
                try:
                    continue
                except BadRequestKeyError:
                    pass
            if not found:
                try:
                    values[arg] = str(request.args[arg])
                    continue
                except BadRequestKeyError:
                    pass
            if not found:
                try:
                    values[arg] = request.form.get(arg)
                    if values[arg] is not None:
                        continue
                except BadRequestKeyError:
                    pass
            if not found:
                try:
                    values[arg] = request.form[arg]
                    if values[arg] is not None:
                        continue
                except BadRequestKeyError:
                    pass
            if arg not in values:
                raise MissingArgumentException("argument '{}' not not found in {}".format(arg, request.url))
        return values


class Client:
    def __init__(self, host, port, page_root="", crt_file=None):
        logger = get_logger()
        self.host = host
        self.application_page = page_root
        self.port = port
        self.crt_file = crt_file
        logger.debug("host:{}, port:{}".format(host, port))
        if self.crt_file:
            http = "https"
        else:
            http = "http"
        if page_root is None:
            page_root = ""
        self.url = '{}://{}:{}/{}'.format(http, host, port, page_root)

    def send_curl(self, command, values):
        logger = get_logger()
        url = "{}/{}".format(self.url, command)
        logger.debug("Accessing URL: {}".format(url))
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        json_data = json.dumps(values)
        json_data_bytes = json_data.encode('utf-8')  # needs to be bytes
        req.add_header('Content-Length', len(json_data_bytes))

        if self.crt_file:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.load_verify_locations(self.crt_file)
            rtn = urllib.request.urlopen(req, json_data_bytes, context=context)
        else:
            rtn = urllib.request.urlopen(req, json_data_bytes)
        data = json.load(rtn)
        return data, rtn


class SimpleWebServer:
    """
    A simple web server wrapper.  You provide the callback to generate the html
    """
    simple_server: Optional["SimpleWebServer"] = None

    class _SimpleWebServer(BaseHTTPRequestHandler):
        """
        A crude web server
        """
        # noinspection PyPep8Naming
        def do_GET(self):
            """
            Called whenever the web page is visited.  It creates the HTML content for the server

            :return: None
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            SimpleWebServer.simple_server.web_page_function(self)

        def log_message(self, fmt, *args):
            """
            This function exists only to overload the parent function and quiet the log messages

            :param fmt:
            :param args:
            :return:
            """
            return

        def send_html(self, text):
            """
            Converts text (ASCII) to a byte string the web server can display and forwards it to the web server

            :param text: the ASCII text to display in the web server
            :return: None
            """
            self.wfile.write(bytes(text, 'utf-8'))

    def __init__(self, host_name, server_port, web_page_function):
        if SimpleWebServer.simple_server is None:
            self.host_name = host_name
            self.server_port = server_port
            self.web_page_function = web_page_function
        SimpleWebServer.simple_server = self

    def start(self):
        """
        Starts the SimpleWebServer.
        Note that it never returns!!!
        :return:
        """
        print("Server started http://%s:%s" % (self.host_name, self.server_port))
        web_server = HTTPServer((self.host_name, self.server_port), SimpleWebServer._SimpleWebServer)
        try:
            web_server.serve_forever()
        except KeyboardInterrupt:
            pass

        web_server.server_close()
        print("Server stopped.")


def get_host_url():
    """
    This function gets the hostname and IP address

    return: hostname and IP address as a dictionary {'hostname':hostname, 'ip': ip}
    or None if unable to determine them
    """
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return {'hostname': host_name,
                'ip': host_ip
                }
    except Exception as e:
        return None
