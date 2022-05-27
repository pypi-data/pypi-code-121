# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from fastapi.responses import UJSONResponse

from ...extend.error import Ignore
from ...extend.struct import Result

from .middleware import RequestIDMiddleware


class Response(UJSONResponse):

    def __init__(self, content=None, status_code=200, *args, **kwargs):

        self._request_id = RequestIDMiddleware.get_request_id()

        super().__init__(content, status_code, *args, **kwargs)

    def render(self, content):

        return super().render(
            Result(data=content, request_id=self._request_id)
        )


class ErrorResponse(Response, Ignore):

    def __init__(self, code, content=None, status_code=200, **kwargs):

        self._code = code

        Response.__init__(self, content, status_code, **kwargs)
        Ignore.__init__(self, self.body.decode(), layers=-1)

    def render(self, content):

        return UJSONResponse.render(
            self,
            Result(code=self._code, error=content, request_id=self._request_id)
        )
