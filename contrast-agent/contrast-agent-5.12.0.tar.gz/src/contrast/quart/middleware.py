# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from quart import Response

from contrast.agent.assess.rules.config import (
    FlaskSessionAgeRule as QuartSessionAgeRule,
    FlaskSecureFlagRule as QuartSecureFlagRule,
    FlaskHttpOnlyRule as QuartHttpOnlyRule,
)
from contrast.agent.middlewares.route_coverage.common import (
    create_routes,
    build_route,
    get_view_func_for_request,
)
from contrast.asgi.middleware import ASGIMiddleware
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.utils.decorators import fail_quietly


class QuartMiddleware(ASGIMiddleware):
    def __init__(self, app):
        self.quart_app = app
        self.config_rules = [
            QuartSessionAgeRule(),
            QuartSecureFlagRule(),
            QuartHttpOnlyRule(),
        ]

        super().__init__(app.asgi_app, app.name)

    def generate_security_exception_response(self):
        return Response(
            response=self.OVERRIDE_MESSAGE,
            status=SecurityException.STATUS_CODE,
            content_type="text/html",
        )

    def get_route_coverage(self):
        return create_routes(self.quart_app)

    @fail_quietly("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return build_route(view_func.__name__, view_func)

    @fail_quietly("Unable to get Quart view func")
    def get_view_func(self, request):
        return get_view_func_for_request(request, self.quart_app)

    @fail_quietly("Failed to run config scanning rules")
    def _scan_configs(self):
        for rule in self.config_rules:
            rule.apply(self.quart_app)
