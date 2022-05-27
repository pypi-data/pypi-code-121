# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api import Route
from contrast.agent.middlewares.route_coverage.common import build_route
from contrast.agent.middlewares.route_coverage.common import (
    DEFAULT_ROUTE_METHODS,
    get_normalized_uri,
    build_key,
)

DEFAULT_ROUTE_METHODS = DEFAULT_ROUTE_METHODS + ("PUT", "PATCH", "DELETE")


def create_bottle_routes(app):
    """
    Returns all the routes registered to a Bottle app as a dict
    :param app: Bottle app
    :return: dict {route_id:  api.Route}
    """
    routes = {}
    for rule in app.routes:
        view_func = rule.callback
        route = build_route(rule.rule, view_func)
        route_id = str(id(view_func))

        for method_type in DEFAULT_ROUTE_METHODS:
            key = build_key(route_id, method_type)
            routes[key] = Route(
                verb=method_type,
                url=get_normalized_uri(str(rule.rule)),
                route=route,
            )
    return routes
