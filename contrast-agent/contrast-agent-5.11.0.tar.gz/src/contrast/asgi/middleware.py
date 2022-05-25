# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.agent.policy.trigger_node import TriggerNode
from contrast.agent.middlewares.base_middleware import BaseMiddleware
from contrast.agent.asgi import (
    track_scope_sources,
    ASGIRequest,
    ASGIResponse,
)
from contrast.utils.decorators import log_time_cm, cached_property
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)

from contrast.utils import Profiler
from contrast.extern import structlog as logging


logger = logging.getLogger("contrast")

DEFAULT_ASGI_NAME = "asgi_app"


class ASGIMiddleware(BaseMiddleware):
    def __init__(self, asgi_app, app_name=None):
        self.app_name = (
            app_name
            if app_name is not None
            else getattr(asgi_app, "__name__", DEFAULT_ASGI_NAME)
        )

        super().__init__()

        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send) -> None:
        self.request_path = scope.get("path", "")

        with Profiler(self.request_path):
            request = ASGIRequest(scope, receive)
            environ = await request.to_wsgi_environ()

            context = self.should_analyze_request(environ)
            if context:
                with contrast.CS__CONTEXT_TRACKER.lifespan(context):
                    await self.call_with_agent(context, request, send)
                    return

            await self.call_without_agent_async(scope, receive, send)

    async def call_with_agent(self, context, request, send) -> None:
        self.log_start_request_analysis()

        track_scope_sources(context, request.scope)

        try:
            self.prefilter(context)

            response = ASGIResponse(send)
            with log_time_cm("app code and get response"):
                await self.asgi_app(
                    request.scope, request.fake_receive, response.fake_send
                )

            context.extract_response_to_context(response)

            self.postfilter(context)
            self.check_for_blocked(context)
            self.handle_ensure(context, context.request)

            await response.call_send()

        except ContrastServiceException as e:
            # handle_ensure should not be called here
            logger.warning(e)
            await self.call_without_agent_async(
                request.scope, request.original_receive, send
            )
            return
        except Exception as e:
            self.handle_ensure(context, request)
            # TODO: PYT-2127
            _ = self.handle_exception(e)
            return
        finally:
            self.log_end_request_analysis()
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()

    async def call_without_agent_async(self, scope, receive, send) -> None:
        super().call_without_agent()
        await self.asgi_app(scope, receive, send)

    @cached_property
    def trigger_node(self):
        """
        trigger node used by reflected xss postfilter rule
        """
        method_name = self.app_name

        module, class_name, args, instance_method = self._process_trigger_handler(
            self.asgi_app
        )

        return (
            TriggerNode(module, class_name, instance_method, method_name, "RETURN"),
            args,
        )
