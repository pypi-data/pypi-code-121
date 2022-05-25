import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

from ...omniversion import Omniversion

from jinja2 import BaseLoader, Environment

SERVER_HOSTNAME = "localhost"
SERVER_PORT = 8080

TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'template.html.j2')


class OmniversionDashboardServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(directory=os.path.dirname(__file__), *args, **kwargs)

    def do_GET(self):
        if self.path != "/":
            print(self.path)
            return super().do_GET()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        with open(TEMPLATE_FILE) as template_file:
            template_str = template_file.read()
            template = Environment(loader=BaseLoader()).from_string(template_str)
            self.wfile.write(bytes(template.render(data=Omniversion()), "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((SERVER_HOSTNAME, SERVER_PORT), OmniversionDashboardServer)
    print(f"Omniversion dashboard server started at http://{SERVER_HOSTNAME}:{SERVER_PORT}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
