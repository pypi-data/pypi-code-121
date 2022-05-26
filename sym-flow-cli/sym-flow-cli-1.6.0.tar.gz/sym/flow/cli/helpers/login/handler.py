import urllib.parse as parse
from http.server import BaseHTTPRequestHandler
from typing import ClassVar, Type

from ...helpers.global_options import GlobalOptions


class AuthHTTPRequestHandler(BaseHTTPRequestHandler):

    options: ClassVar[GlobalOptions]
    state: ClassVar[str]
    auth_code: ClassVar[str]

    def log_message(self, format, *args):
        ...

    def do_GET(self):
        parsed = parse.urlparse(self.path)
        qs = parse.parse_qs(parsed.query)

        if not "code" in qs:
            self.send_error(401, explain="Missing code in query")
            return

        if not "state" in qs:
            self.send_error(401, explain="Missing state in query")
            return

        [returned_state] = qs["state"]
        if not returned_state == self.__class__.state:
            self.__class__.options.dprint(
                f"Invalid state. Found: {returned_state}, expected: {self.__class__.state}."
            )
            self.send_error(401, explain="Invalid state")
            return

        [returned_code] = qs["code"]

        self.send_response(301)
        self.send_header("Location", "https://static.symops.com/cli/login")
        self.end_headers()

        self.__class__.auth_code = returned_code


def make_handler(options: GlobalOptions, state: str) -> Type[AuthHTTPRequestHandler]:
    class Handler(AuthHTTPRequestHandler):
        ...

    Handler.options = options
    Handler.state = state
    return Handler
