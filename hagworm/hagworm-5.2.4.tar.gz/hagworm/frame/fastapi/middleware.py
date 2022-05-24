# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from contextvars import ContextVar

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ...extend.base import Utils


REQUEST_ID_CONTEXT = ContextVar(r'request_id')


class RequestIDMiddleware:

    @staticmethod
    def get_request_id():

        return REQUEST_ID_CONTEXT.get(None)

    def __init__(self, app: ASGIApp) -> None:

        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:

        responder = _Response(self._app)

        await responder(scope, receive, send)


class _Response:

    def __init__(self, app: ASGIApp):

        self._app = app
        self._send = None

        self._request_id = Utils.uuid1_urn()
        self._request_time = Utils.timestamp(True)

        REQUEST_ID_CONTEXT.set(self._request_id)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):

        self._send = send

        await self._app(scope, receive, self.send)

    async def send(self, message: Message) -> None:

        message.setdefault(r'headers', [])

        message[r'headers'].append((b'x-delayed', str(Utils.timestamp(True) - self._request_time).encode(r'latin-1')))
        message[r'headers'].append((b'x-timestamp', str(Utils.timestamp(True)).encode(r'latin-1')))
        message[r'headers'].append((b'x-request-id', self._request_id.encode(r'latin-1')))

        await self._send(message)
