# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from io import BytesIO

from contrast.agent import scope as scope_
from contrast.agent.assess.policy.analysis import skip_analysis
from contrast.agent.assess.policy.source_policy import (
    cs__apply_source,
    build_source_node,
)
from contrast.utils.decorators import fail_loudly, cached_property
from contrast.extern.webob.headers import ResponseHeaders

# note: request method is not a source, per labs
# source types translated from environ sources in environ_tracker.py
SCOPE_SOURCES = {
    "path": "URI",
    "raw_path": "URI",
    "query_string": "QUERYSTRING",
    "root_path": "OTHER",
    "server": "OTHER",
    "client": "OTHER",
    "headers": "HEADER",
    "cookie": "COOKIE",  # not an actual scope element; we use this for headers[cookie]
}

SOURCE_DICT = {"module": "ASGI.scope", "instance_method": False, "target": "RETURN"}
EVENT_TYPE = "http.request"


class ASGIRequest:
    """
    A barebones request class for ASGI applications. This class is mostly useful for
    managing the `receive` coroutine, which is how ASGI apps get the request body.
    """

    def __init__(self, scope, original_receive):
        self.scope = scope
        self.original_receive = original_receive

        self._called = False
        self._body = None
        self._wsgi_environ = None

    async def fake_receive(self):
        """
        This coroutine should be sent to the underlying ASGI application instead of the
        original `receive`. This allows us to capture the request body while still
        providing the ASGI app with a valid `receive`-like coroutine.
        """
        if self._called:
            return {"type": "http.disconnect"}

        body = await self.body()
        self._called = True
        return {
            "type": EVENT_TYPE,
            "body": body,
            "more_body": False,
        }

    async def body(self):
        """
        Call the original `receive` coroutine and store the result. This coroutine can
        be called multiple times without adverse consequences.
        """
        if self._body is not None:
            return self._body

        body_parts = []
        more_body = True
        while more_body:
            event = await self.original_receive()
            if event["type"] == EVENT_TYPE:
                body_parts.append(event.get("body", b""))
                more_body = event.get("more_body", False)
            else:
                more_body = False
        self._body = b"".join(body_parts)
        return self._body

    async def to_wsgi_environ(self):
        if self._wsgi_environ is not None:
            return self._wsgi_environ

        body = await self.body()
        self._wsgi_environ = _scope_to_environ(self.scope, body)
        return self._wsgi_environ


class ASGIResponse:
    """
    A Response class for ASGI applications. This class handles everything related to the
    `send` coroutine, which is how ASGI applications send response data.
    """

    def __init__(self, original_send):
        self._original_send = original_send
        self._response_started = False
        self._more_body = True
        self._status_code = None
        self._asgi_headers = []
        self._body_parts = []

    async def fake_send(self, event):
        """
        This is a heavily simplified version of the actual `send` implementation from
        Uvicorn.

        `send` is the function that the application uses to send data back to the client
        - by replacing it, we can analyze and control the response. Instead of actually
        sending data anywhere, this method simply stores the response content on our
        ASGIResponse object.
        """
        event_type = event["type"]
        if not self._response_started and self._more_body:
            if event_type != "http.response.start":
                raise RuntimeError(
                    f"Expected ASGI event http.response.start but got '{event_type}'"
                )
            self._response_started = True
            self._status_code = event["status"]
            self._asgi_headers = event.get("headers", [])
        elif self._more_body:
            if event_type != "http.response.body":
                raise RuntimeError(
                    f"Expected ASGI event http.response.body but got '{event_type}'"
                )
            self._body_parts.append(event.get("body", b""))
            self._more_body = event.get("more_body", False)
        else:
            raise RuntimeError(
                f"Unexpected ASGI event '{event_type}' after response already completed"
            )

    # TODO: PYT-2127 - it's possible that we may want to change these properties around
    # to make them writeable
    @cached_property
    def body(self):
        self._check_more_body()
        return b"".join(self._body_parts)

    @cached_property
    def headers(self):
        """
        To comply with our internal ResponseWrapper API, we need headers to be strings,
        not bytes
        """
        self._check_response_started()
        return ResponseHeaders(
            [(key.decode(), value.decode()) for key, value in self._asgi_headers]
        )

    @cached_property
    def status_code(self):
        self._check_response_started()
        return self._status_code

    async def call_send(self):
        """
        Call the original `send` method we captured from the server using the
        response information we captured from the application.
        """
        await self._original_send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self._asgi_headers,
            }
        )
        await self._original_send(
            {
                "type": "http.response.body",
                "body": self.body,
                "more_body": False,
            }
        )

    def _check_more_body(self):
        if self._more_body:
            raise RuntimeError(f"ASGI application did not finish sending response body")

    def _check_response_started(self):
        if not self._response_started:
            raise RuntimeError(f"ASGI application did not start response")


@fail_loudly("Failed to convert starlette request to environ dict")
async def starlette_request_to_environ(request):
    body = await _get_body_non_destructive(request)
    return _scope_to_environ(request.scope, body)


async def _get_body_non_destructive(request) -> bytes:
    """
    Get the request body without consuming the ASGI `receive` callable. This involves
    some trickery. We bank on the fact that we're in a starlette / fastAPI environment,
    which uses `call_next` for each successive middleware.

    In the general ASGI case, we will need to perform all of the work currently done in
    request.body(), then send our replaced_receive function to the next middleware or
    application when we call it.
    """
    body = await request.body()
    called = False

    async def replaced_receive():
        # On the first call, send the whole body
        # On successive calls, send the disconnect message
        nonlocal called
        if not called:
            called = True
            return {
                "type": EVENT_TYPE,
                "body": body,
                "more_body": False,
            }
        return {"type": "http.disconnect"}

    request._receive = replaced_receive
    return body


def _scope_to_environ(scope: dict, body: bytes) -> dict:
    """
    Convert an asgi `scope` into a wsgi `environ` dict

    Copied from https://github.com/django/asgiref/blob/main/asgiref/wsgi.py
    and modified to our needs
    """
    environ = {
        "REQUEST_METHOD": scope["method"],
        "SCRIPT_NAME": scope.get("root_path", "").encode("utf8").decode("latin1"),
        "PATH_INFO": scope["path"].encode("utf8").decode("latin1"),
        "QUERY_STRING": scope["query_string"].decode("ascii"),
        "SERVER_PROTOCOL": f"HTTP/{scope['http_version']}",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": scope.get("scheme", "http"),
        "wsgi.input": BytesIO(body),
        "wsgi.errors": BytesIO(),
        "wsgi.multithread": True,
        "wsgi.multiprocess": True,
        "wsgi.run_once": False,
    }

    # Get server name and port - required in WSGI, not in ASGI
    if "server" in scope:
        environ["SERVER_NAME"] = scope["server"][0]
        environ["SERVER_PORT"] = str(scope["server"][1] or 80)
    else:
        environ["SERVER_NAME"] = "localhost"
        environ["SERVER_PORT"] = "80"

    if "client" in scope:
        environ["REMOTE_ADDR"] = scope["client"][0]

    # Go through headers and make them into environ entries
    for name, value in scope.get("headers", []):
        name = name.decode("latin1")
        if name == "content-length":
            corrected_name = "CONTENT_LENGTH"
        elif name == "content-type":
            corrected_name = "CONTENT_TYPE"
        else:
            corrected_name = f"HTTP_{name.upper().replace('-', '_')}"
        # HTTPbis say only ASCII chars are allowed in headers, but we latin1 just in
        # case
        value = value.decode("latin1")
        if corrected_name in environ:
            value = environ[corrected_name] + "," + value
        environ[corrected_name] = value

    return environ


def track_scope_sources(context, scope):
    """
    Iterate over the ASGI scope and explicitly track all relevant values. This is
    similar to the environ tracker. This function does not track the request body, which
    comes from the receive awaitable.

    There's an unfortunate possibility of starlette's request object having already
    cached some data from the scope dict. The easiest way around this would be to find
    and clear all of the places where starlette might save these variables. This could
    be avoided by going for an approach that's closer to pure ASGI instead of relying as
    much on starlette.

    @param context: the current request context
    @param scope: the ASGI scope dict
    """
    if skip_analysis(context):
        return

    with scope_.contrast_scope():
        for key, value in scope.items():
            if key in ["client", "server"]:
                for elem in value:
                    _track_scope_item(context, scope, key, elem)
            elif key == "headers":
                for header_key, header_value in value:
                    if header_key == b"cookie":
                        key = "cookie"
                    _track_scope_item(context, scope, key, header_key)
                    _track_scope_item(context, scope, key, header_value)
            else:
                _track_scope_item(context, scope, key, value)


def _track_scope_item(context, scope, key, value):
    # there are other elements in `scope`, but only those in SCOPE_SOURCES matter to us
    if key in SCOPE_SOURCES:
        node = build_source_node(SOURCE_DICT, key, SCOPE_SOURCES[key], "ASGI")
        cs__apply_source(context, node, value, scope, value, (), {}, source_name=key)
