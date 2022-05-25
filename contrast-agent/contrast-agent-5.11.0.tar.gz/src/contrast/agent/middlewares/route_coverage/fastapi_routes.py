# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api import Route
from contrast.agent.middlewares.route_coverage.common import (
    DEFAULT_ROUTE_METHODS,
    get_normalized_uri,
    build_key,
)
from contrast.agent.middlewares.route_coverage.common import build_route

DEFAULT_ROUTE_METHODS = DEFAULT_ROUTE_METHODS + ("HEAD",)


def create_fastapi_routes(app):
    """
    Returns all the routes registered to a FastAPI app as a dict
    :param app: FastAPI app instance
    :return: dict {route_id:  api.Route}
    """
    routes = {}

    for app_route in app.routes:
        view_func = app_route.endpoint
        route = build_route(app_route.name, view_func)
        route_id = str(id(view_func))
        methods = app_route.methods or DEFAULT_ROUTE_METHODS

        for method_type in methods:
            key = build_key(route_id, method_type)
            routes[key] = Route(
                verb=method_type,
                url=get_normalized_uri(str(app_route.name)),
                route=route,
            )

    return routes
