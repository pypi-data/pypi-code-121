# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api import Route
from contrast.agent.middlewares.route_coverage.common import (
    build_route,
    get_normalized_uri,
    build_key,
)

from aiohttp.web_urldispatcher import DynamicResource


def create_aiohttp_routes(app):
    """
    Returns all the routes registered to a AioHttp app as a dict
    :param app: AioHttp app instance
    :return: dict {route_id:  api.Route}
    """
    routes = {}

    for app_route in app.router._resources:
        for resource in app_route._routes:

            view_func = resource.handler
            name = view_func.__name__
            route = build_route(name, view_func)

            route_id = str(id(view_func))

            _route_attr = (
                app_route._formatter
                if isinstance(app_route, DynamicResource)
                else app_route._path
            )
            method_type = resource.method
            key = build_key(route_id, method_type)
            routes[key] = Route(
                verb=method_type,
                url=get_normalized_uri(_route_attr),
                route=route,
            )

    return routes
