# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.webob import Request, Response

import contrast
from contrast.agent.policy.trigger_node import TriggerNode
from contrast.agent.middlewares.base_middleware import BaseMiddleware
from contrast.agent.middlewares.environ_tracker import track_environ_sources
from contrast.utils.decorators import cached_property, fail_quietly, log_time_cm
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)

from contrast.extern import structlog as logging
from contrast.utils import Profiler

logger = logging.getLogger("contrast")
DEFAULT_WSGI_NAME = "wsgi_app"


class WSGIMiddleware(BaseMiddleware):
    """
    Contrast middleware; PEP-333(3) WSGI-compliant
    """

    def __init__(self, wsgi_app, app_name=None):
        if app_name:
            self.app_name = app_name
        elif hasattr(wsgi_app, "__name__"):
            self.app_name = wsgi_app.__name__
        else:
            self.app_name = DEFAULT_WSGI_NAME

        super().__init__()

        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        self.request_path = environ.get("PATH_INFO", "")

        with Profiler(self.request_path):
            context = self.should_analyze_request(environ)
            if context:
                with contrast.CS__CONTEXT_TRACKER.lifespan(context):
                    return self.call_with_agent(context, environ, start_response)

            return self.call_without_agent(environ, start_response)

    def call_with_agent(self, context, environ, start_response):
        self.log_start_request_analysis()

        track_environ_sources("wsgi", context, environ)

        try:
            self.prefilter(context)

            with log_time_cm("app code and get response"):
                # this returns a webob response class, which already
                # implements BaseResponseWrapper's requirements
                response = Request(environ).get_response(self.wsgi_app)

            context.extract_response_to_context(response)

            self.postfilter(context)
            self.check_for_blocked(context)
            self.swap_environ_path(environ)  # should not be moved to finally
            self.handle_ensure(context, context.request)

            return response(environ, start_response)

        except ContrastServiceException as e:
            # handle_ensure should not be called here
            self.swap_environ_path(environ)  # should not be moved to finally
            logger.warning(e)
            return self.call_without_agent(environ, start_response)
        except Exception as e:
            self.swap_environ_path(environ)  # should not be moved to finally
            self.handle_ensure(context, context.request)
            response = self.handle_exception(e)
            return response(environ, start_response)
        finally:
            self.log_end_request_analysis()
            if self.settings.is_assess_enabled():
                contrast.STRING_TRACKER.ageoff()

    def swap_environ_path(self, environ):
        """
        See PYT-1742.

        Special behavior required for bottle+django to account for an unfortunate
        encoding behavior.

        In bottle, it occurs here:
        bottle.py:
        def _handle(self, environ):
            ...
            environ['PATH_INFO'] = path.encode('latin1').decode('utf8')
            ...

        This casing occurs after the application code is called, and will result in a
        `UnicodeEncodeError` when the agent attempts to access request.path.
        As a workaround, we store the original PATH_INFO - before bottle changed it
        during calling app code - and use it for agent purposes.
        """
        environ["PATH_INFO"] = self.request_path

    def generate_security_exception_response(self):
        return Response(self.OVERRIDE_MESSAGE, SecurityException.STATUS)

    def call_without_agent(self, environ, start_response):
        """
        Normal without middleware call
        """
        super().call_without_agent()
        return self.wsgi_app(environ, start_response)

    def get_route_coverage(self):
        """
        Unlike frameworks, WSGI is a spec, so it does not have a way to register routes.
        As such, there is no way to discover routes. Instead, routes will be added as
        they are visited via check for new routes.

        :return: empty dict
        """
        return {}

    @cached_property
    def trigger_node(self):
        """
        WSGI-specific trigger node used by reflected xss postfilter rule

        The rule itself is implemented in the base middleware but we need to
        provide a WSGI-specific trigger node for reporting purposes.
        """
        method_name = self.app_name

        module, class_name, args, instance_method = self._process_trigger_handler(
            self.wsgi_app
        )

        return (
            TriggerNode(module, class_name, instance_method, method_name, "RETURN"),
            args,
        )

    @fail_quietly("Unable to get WSGI view func")
    def get_view_func(self, _):
        """
        While most frameworks define view functions, WSGI doesn't so we will rely
        on the path information for reporting.
        If there is no path information, return an empty string

        :param request: RequestContext instance
        :return: string of path information for this request
        """
        return self.request_path or None

    @fail_quietly("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return url.replace("/", "")
