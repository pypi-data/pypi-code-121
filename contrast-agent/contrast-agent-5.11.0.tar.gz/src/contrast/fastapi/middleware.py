# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.agent import scope as scope_
from contrast.agent.policy.trigger_node import TriggerNode
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from contrast.agent.middlewares.base_middleware import BaseMiddleware
from contrast.agent.middlewares.app_finder import get_original_app_or_fail
from contrast.agent.middlewares.response_wrappers.fastapi_response_wrapper import (
    FastApiResponseWrapper,
)
from contrast.agent.middlewares.route_coverage.fastapi_routes import (
    create_fastapi_routes,
)
from contrast.agent.middlewares.route_coverage.common import build_route
from contrast.agent.asgi import starlette_request_to_environ, track_scope_sources
from contrast.extern import structlog as logging
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.utils.decorators import cached_property, fail_quietly, log_time_cm
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)

from contrast.utils.string_utils import ensure_binary
from contrast.utils import Profiler

logger = logging.getLogger("contrast")


class FastApiMiddleware(BaseMiddleware, BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, original_app: FastAPI = None) -> None:
        self.app = app
        self.original_app = (
            original_app
            if original_app is not None and isinstance(original_app, FastAPI)
            else get_original_app_or_fail(app, FastAPI)
        )
        self.app_name = self.original_app.title

        self.dispatch_func = self.agent_dispatch_func

        super().__init__()

    async def agent_dispatch_func(self, request: Request, call_next):
        """
        Instead of implementing a __call__ function, we rely on
        BaseHTTPMiddleware's __call__ func which calls self.dispatch_func.
        """
        self.request_path = request.scope.get("path", "")

        with Profiler(self.request_path):
            with scope_.contrast_scope():
                environ = await starlette_request_to_environ(request)

            context = self.should_analyze_request(environ)
            if context:
                with contrast.CS__CONTEXT_TRACKER.lifespan(context):
                    return await self.call_with_agent(context, request, call_next)

            return await self.call_without_agent_async(request, call_next)

    async def call_without_agent_async(self, request: Request, call_next):
        super().call_without_agent()
        return await call_next(request)

    async def call_with_agent(self, context, request: Request, call_next):
        scope = request.scope
        self.log_start_request_analysis()

        track_scope_sources(context, scope)
        try:
            self.prefilter(context)

            with log_time_cm("app code and get response"):
                response = await call_next(request)

            with scope_.contrast_scope():
                wrapped_response = FastApiResponseWrapper(response)

            await self.extract_response_to_context_async(wrapped_response, context)

            self.postfilter(context)
            self.check_for_blocked(context)
            self.handle_ensure(context, context.request)
            return response

        except ContrastServiceException as e:
            # handle_ensure should not be called here
            logger.warning(e)
            return await self.call_without_agent_async(request, call_next)
        except Exception as e:
            self.handle_ensure(context, context.request)
            response = self.handle_exception(e)
            return response
        finally:
            self.log_end_request_analysis()
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()

    @fail_quietly("Unable to get route coverage", return_value={})
    def get_route_coverage(self):
        return create_fastapi_routes(self.original_app)

    @fail_quietly("Unable to get FastAPI view func")
    def get_view_func(self, request):
        if not self.request_path:
            return None

        # Checking for `==` works here because fastapi correctly re-routes
        # if user adds (or doesn't) a /. So this method may be called
        # multiple times per request.
        matching_routes = [
            x for x in self.original_app.routes if x.path == self.request_path
        ]

        if not matching_routes:
            return None

        view_func = matching_routes[0].endpoint
        return view_func

    @fail_quietly("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return build_route(url, view_func)

    def generate_security_exception_response(self):
        return PlainTextResponse(self.OVERRIDE_MESSAGE, SecurityException.STATUS_CODE)

    @cached_property
    def trigger_node(self):
        """
        FastAPI-specific trigger node used by reflected xss postfilter rule
        """
        method_name = self.app_name

        module, class_name, args, instance_method = self._process_trigger_handler(
            self.original_app
        )

        return (
            TriggerNode(module, class_name, instance_method, method_name, "RETURN"),
            args,
        )

    async def extract_response_to_context_async(self, response, context):
        """
        Async method to extract response information.
        Unlike the similarly named method in RequestContext, we define
        this method here because defining any async method in RequestContext
        causes SyntaxError for Py2. We can move this once we deprecate Py2.
        """
        context.response = response

        if not self.settings.response_scanning_enabled:
            return

        context.activity.http_response.response_code = response.status_code

        for key, values in response.headers.dict_of_lists().items():
            normalized_key = key.upper().replace("-", "_")
            response_headers = (
                context.activity.http_response.normalized_response_headers
            )
            response_headers[normalized_key].key = key
            response_headers[normalized_key].values.extend(values)

        await response.body_async

        context.activity.http_response.response_body_binary = ensure_binary(
            response.body or ""
        )
