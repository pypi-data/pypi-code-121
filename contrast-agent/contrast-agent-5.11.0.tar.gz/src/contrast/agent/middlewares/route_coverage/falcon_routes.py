# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import copy
from contrast.api import Route

from contrast.agent.middlewares.route_coverage.common import (
    DEFAULT_ROUTE_METHODS,
    build_args_from_function,
    build_key,
    get_normalized_uri,
)

DEFAULT_ROUTE_METHODS = copy.copy(DEFAULT_ROUTE_METHODS) + ("PUT", "PATCH", "DELETE")


def create_falcon_routes(app):
    """
    Given a Falcon app instance, use the private router
    to find all register routes. At this time, Falcon
    does not have a public API to get the app's routes.

    Borrowed from: https://stackoverflow.com/a/54510794

    :param app: class falcon.API or class falcon.APP instance
    :return: dict {route_id:  api.Route
    """
    routes = {}

    def get_children(node):
        if len(node.children):
            for child_node in node.children:
                get_children(child_node)
        else:
            create_routes(node.resource, node.uri_template, routes)

    for node in app._router._roots:
        get_children(node)

    return routes


def create_routes(endpoint_cls, path, routes):
    """
    Add to routes new items representing view functions for
    falcon class endpoint.

    :param endpoint_cls: Falcon class that defines views
    :param path: string of url path such as /home
    :param routes: dict of routes
    :return: None, side effect appends to routes
    """
    for method in DEFAULT_ROUTE_METHODS:
        view_func = get_view_method(endpoint_cls, method)

        if view_func:

            route = build_falcon_route(view_func, endpoint_cls)

            route_id = build_key(str(id(view_func)), method)
            routes[route_id] = Route(
                verb=method,
                url=get_normalized_uri(str(path)),
                route=route,
            )


def get_view_method(cls_instance, request_method):
    """
    Falcon defines views like this
    ```
    class Cmdi(object):
        def on_get(self, request, response):
            response.status = falcon.HTTP_200
            response.body = "Result from CMDI"
    ```
    Given this class definition and the request_method string,
    we will look for the correct view method.

    Note that we need to get the unbound method because later on we
    will get the id of this method.

    :param cls_instance: instance of Falcon class endpoint such as Cmdi in the above example
    :param request_method: string such as GET or POST
    :return: function: view method for the request_method, such as on_get for example above
    """
    view_name = f"on_{request_method.lower()}"
    if hasattr(cls_instance, view_name):
        # use .__class__ and/or __func__ to get the unbound method
        view_func = getattr(cls_instance.__class__, view_name)

        return view_func

    return None


def build_falcon_route(view_func, endpoint_cls):
    route_args = build_args_from_function(view_func)
    route = f"{endpoint_cls.__class__.__name__}.{view_func.__name__}{route_args}"
    return route
