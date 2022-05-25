# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api import Finding, Route
from contrast.utils.decorators import log_time
from contrast.agent.middlewares.route_coverage.common import build_key

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class RoutesMixin(object):
    """
    Class for route coverage work.
    Route coverage is assess only.
    """

    @log_time("route coverage")
    def handle_routes(self, context, request):
        """
        Method that should run for all middlewares immediately after the application executes.
        """
        if context and request:
            self.get_routes_on_first_request()

            self.check_for_new_routes(context, request)

            self.append_route_to_findings(context)

    def get_routes_on_first_request(self):
        """
        Attempt to do route discovery on the first request
        """
        if not self.first_request:
            return

        logger.debug("First request so looking for app routes.")

        routes = self.get_route_coverage()

        if not routes or not isinstance(routes, dict):
            logger.debug("Could not find any routes")
        else:
            self.routes = routes

            routes_to_log = [
                f"{route.verb}: {route.url}" for route in self.routes.values()
            ]
            logger.debug("Found the following routes: %s", routes_to_log)

    def check_for_new_routes(self, context, request):
        """
        We check for new routes (in addition to the ones already in self.routes which
        were found through looking for expected routes the app registered during the first request.

        This instead looks to see if the current request is a new route we should add
        to middleware routes.
        """
        logger.debug("Checking for new route.")

        func = self.get_view_func(request)
        if func is None:
            return

        request_method = request.method
        route_id = build_key(str(id(func)), request_method)

        self.update_route_information(context, route_id, request_method, func)

    def update_route_information(self, context, route_id, request_method, func):
        """
        Given a context and route_id, check if the route_id is in middleware (self) routes.
        Store the route as current and observed route for later use.

        :param context: RequestContext instance
        :param route_id: string id for a route
        :param request_method: string such as 'GET'
        :param func:  App view function
        :return: no return, side effects only
        """
        if route_id not in self.routes:
            self.extend_middleware_routes(
                request_method, context.request.get_normalized_uri(), route_id, func
            )

        route = self.routes[route_id]

        logger.debug("Route visited: %s : %s", route.verb, route.url)

        # save current route as a dtm; this is used to append to findings
        context.current_route = route.to_dtm()

        # Currently we do not report an observed route if the route signature is empty.
        # As a team we've decided there isn't a meaningful default signature value
        # we can provide to customers. If a route doesn't show up in Contrast UI,
        # it may be due to its missing signature. In this scenario, we will have to work
        # with the customer directly to understand why the signature was not created.
        if not route.signature:
            logger.debug(
                "No route signature found for %s : %s (id=%s). Not updating observed"
                " route",
                route.verb,
                route.url,
                route_id,
            )
            return

        context.observed_route.signature = route.signature

        context.observed_route.url = route.url
        context.observed_route.verb = route.verb

    def extend_middleware_routes(self, request_method, url, route_id, func):
        route = self.build_route(func, url)
        self.routes[route_id] = Route(verb=request_method, url=url, route=route)

    def append_route_to_findings(self, context):
        """
        Route discovery and current route is not identified until the handle ensure
        part of the request lifecycle, after assess has analyzed and potentially created
        a finding, so that is why we have to append the now-available current route to
        the existing finding.
        """
        if not context.current_route:
            logger.debug("No current route to append to findings")
            return

        if not context.activity.findings:
            logger.debug("No findings to append route to")
            return

        for finding in context.activity.findings:
            if not finding.routes:
                logger.debug(
                    "Appending route %s:%s to %s",
                    context.current_route.verb,
                    context.current_route.url,
                    finding.rule_id,
                )
                finding.routes.extend([context.current_route])

            finding.version = Finding.pick_version(finding)

    def get_view_func(self, request):
        return

    def build_route(self, view_func, url):
        return ""
