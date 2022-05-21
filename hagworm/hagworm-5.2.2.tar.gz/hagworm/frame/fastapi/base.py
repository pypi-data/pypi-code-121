# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import fastapi

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.exceptions import HTTPException
from starlette.routing import iscoroutinefunction_or_partial
from starlette.concurrency import run_in_threadpool

from fastapi import __version__ as fastapi_version
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html

from ... import hagworm_label, hagworm_slogan
from ... import __version__ as hagworm_version

from ...extend.asyncio.base import Utils, install_uvloop
from ...extend.logging import DEFAULT_LOG_FILE_NAME, DEFAULT_LOG_FILE_ROTATOR, init_logger

from .response import Response, ErrorResponse
from .middleware import RequestIDMiddleware


get_swagger_ui_html.__kwdefaults__.update(
    {
        r'swagger_js_url': r'https://cdn.staticfile.org/swagger-ui/4.11.1/swagger-ui-bundle.min.js',
        r'swagger_css_url': r'https://cdn.staticfile.org/swagger-ui/4.11.1/swagger-ui.min.css',
    }
)


DEFAULT_HEADERS = [(r'Server', hagworm_label)]


def create_fastapi(
        log_level=r'info', log_handler=None, log_file_path=None, log_file_name=DEFAULT_LOG_FILE_NAME,
        log_file_rotation=DEFAULT_LOG_FILE_ROTATOR, log_file_retention=0xff,
        debug=False,
        routes=None,
        **setting
):

    init_logger(
        log_level.upper(),
        log_handler,
        log_file_path,
        log_file_name,
        log_file_rotation,
        log_file_retention,
        debug
    )

    environment = Utils.environment()

    Utils.log.info(
        f'{hagworm_slogan}'
        f'hagworm {hagworm_version}\n'
        f'fastapi {fastapi_version}\n'
        f'python {environment["python"]}\n'
        f'system {" ".join(environment["system"])}'
    )

    setting.setdefault(r'title', r'Hagworm')
    setting.setdefault(r'version', hagworm_version)

    install_uvloop()

    _fastapi = fastapi.FastAPI(debug=debug, routes=routes, **setting)

    _fastapi.add_middleware(RequestIDMiddleware)

    _fastapi.add_exception_handler(HTTPException, http_exception_handler)
    _fastapi.add_exception_handler(RequestValidationError, request_validation_exception_handler)

    return _fastapi


class APIRoute(fastapi.routing.APIRoute):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.app = self.request_response()

    async def prepare(self, request):

        pass

    def request_response(self) -> ASGIApp:

        func = self.get_route_handler()

        is_coroutine = iscoroutinefunction_or_partial(func)

        async def app(scope: Scope, receive: Receive, send: Send) -> None:

            try:

                request = Request(scope, receive, send, self)

                await self.prepare(request)

                if is_coroutine:
                    response = await func(request)
                else:
                    response = await run_in_threadpool(func, request)

                await response(scope, receive, send)

            except ErrorResponse as err:

                Utils.log.warning(f'ErrorResponse: {request.path}\n{err}\n{request.debug_info}')

                await err(scope, receive, send)

        return app


class APIRouter(fastapi.APIRouter):
    """目录可选末尾的斜杠访问
    """

    def __init__(
            self,
            *,
            prefix=r'',
            default_response_class=Response,
            route_class=APIRoute,
            **kwargs
    ):

        super().__init__(
            prefix=prefix,
            default_response_class=default_response_class,
            route_class=route_class,
            **kwargs
        )

    def _get_path_alias(self, path):

        _path = path.rstrip(r'/')

        if not self.prefix and not _path:
            return [path]

        _path_split = os.path.splitext(_path)

        if _path_split[1]:
            return [_path]

        return [_path, _path + r'/']

    def api_route(self, path, *args, **kwargs):

        def _decorator(func):

            for index, _path in enumerate(self._get_path_alias(path)):

                self.add_api_route(_path, func, *args, **kwargs)

                # 兼容的URL将不会出现在docs中
                if index == 0:
                    kwargs[r'include_in_schema'] = False

            return func

        return _decorator


class Request(fastapi.Request):

    def __init__(self, scope: Scope, receive: Receive, send: Send, api_route: APIRoute):

        super().__init__(scope, receive, send)

        self._api_route = api_route

        self._request_id = RequestIDMiddleware.get_request_id()

    @property
    def request_id(self):

        return self._request_id

    @property
    def debug_info(self):

        return {
            'request_id': self._request_id,
            'type': self.scope.get(r'type'),
            'http_version': self.scope.get(r'http_version'),
            'server': self.scope.get(r'server'),
            'client': self.scope.get(r'client'),
            'scheme': self.scope.get(r'scheme'),
            'method': self.scope.get(r'method'),
            'root_path': self.scope.get(r'root_path'),
            'path': self.scope.get(r'path'),
            'query_string': self.scope.get(r'query_string'),
            'headers': self.scope.get(r'headers'),
        }

    @property
    def route(self):

        return self._api_route

    @property
    def path(self):

        return self._api_route.path

    @property
    def tags(self):

        return self._api_route.tags

    @property
    def referer(self):

        return self.headers.get(r'Referer')

    @property
    def client_ip(self):

        if self.x_forwarded_for:
            return self.x_forwarded_for[0]
        else:
            return self.client_host

    @property
    def client_host(self):

        return self.headers.get(r'X-Real-IP', self.client.host)

    @property
    def x_forwarded_for(self):

        return Utils.split_str(self.headers.get(r'X-Forwarded-For', r''), r',')

    @property
    def content_type(self):

        return self.headers.get(r'Content-Type')

    @property
    def content_length(self):

        result = self.headers.get(r'Content-Length', r'')

        return int(result) if result.isdigit() else 0

    def get_header(self, name, default=None):

        return self.headers.get(name, default)


async def http_exception_handler(
        request: Request, exc: HTTPException
) -> ErrorResponse:

    headers = getattr(exc, r'headers', None)

    if headers:
        return ErrorResponse(
            -1,
            content={r'detail': exc.detail},
            status_code=exc.status_code,
            headers=headers
        )
    else:
        return ErrorResponse(
            -1,
            content={r'detail': exc.detail},
            status_code=exc.status_code
        )


async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> ErrorResponse:

    return ErrorResponse(
        -1,
        content={r'detail': jsonable_encoder(exc.errors())},
        status_code=HTTP_400_BAD_REQUEST,
    )
