# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.wsgi.middleware import WSGIMiddleware
from contrast.agent.middlewares.app_finder import get_original_app_or_fail
from contrast.utils.decorators import fail_quietly
from contrast.extern import structlog as logging
from contrast.agent.middlewares.route_coverage.bottle_routes import create_bottle_routes
from contrast.agent.middlewares.route_coverage.common import build_route
import bottle

logger = logging.getLogger("contrast")


class BottleMiddleware(WSGIMiddleware):
    # Since Bottle is WSGI-based, there is no way to retrieve the app name.
    # Use common config to define an app name.
    def __init__(self, app, orig_bottle_app=None):
        _app = (
            orig_bottle_app
            if orig_bottle_app is not None
            and isinstance(orig_bottle_app, bottle.Bottle)
            else get_original_app_or_fail(app, bottle.Bottle)
        )
        super().__init__(_app, app_name="Bottle Application")

    @fail_quietly("Unable to get route coverage", return_value={})
    def get_route_coverage(self):
        return create_bottle_routes(self.wsgi_app)

    @fail_quietly("Unable to get Bottle view func")
    def get_view_func(self, request):
        path = request.path
        if not path:
            return None
        method = request.method
        route_info = self.wsgi_app.match({"PATH_INFO": path, "REQUEST_METHOD": method})
        if not route_info:
            return None
        view_func = route_info[0].callback
        return view_func

    @fail_quietly("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return build_route(url, view_func)
