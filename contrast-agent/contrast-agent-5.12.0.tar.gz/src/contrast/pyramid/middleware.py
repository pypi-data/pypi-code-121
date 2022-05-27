# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.middlewares.route_coverage.pyramid_routes import PyramidRoutesMixin
from contrast.wsgi.middleware import WSGIMiddleware
from contrast.agent.middlewares.app_finder import get_original_app_or_fail
from contrast.extern import structlog as logging
from contrast.utils.decorators import fail_quietly

from pyramid.registry import Registry

logger = logging.getLogger("contrast")


class PyramidWSGIMiddleware(PyramidRoutesMixin, WSGIMiddleware):
    """
    A subclass of the WSGI middleware that provides pyramid route coverage.
    "configuration scanning" in pyramid is handled dynamically with triggers.

    This is not a pyramid-style tween - it must wrap pyramid's WSGI application
    directly. The WSGI app is typically returned by a call to some Configurator
    instance's `make_wsgi_app()`.
    """

    def __init__(self, wsgi_app, orig_pyramid_registry=None):
        """
        This deviates slightly from typical WSGI Middleware API, because we need
        `registry` to get framework-specific information about the application.

        The application's `Registry` is commonly available as an attribute on the
        `Configurator` instance used to construct the application. It is also available
        as an attribute of the original WSGI application object returned by
        `Configurator.make_wsgi_app()`. Note that we can't guarantee that the WSGI app
        passed to this constructor has a `registry` attribute, since the original
        Pyramid WSGI app might have already been wrapped by other WSGI middlewares.

        @param wsgi_app: a WSGI application object for the Pyramid application to be
            instrumented by Contrast
        @param registry: (optional) the `pyramid.registry.Registry` instance
            corresponding to the wsgi_app - if not provided, we make a best effort to
            find it on the provided app
        """
        self.registry = (
            orig_pyramid_registry
            if orig_pyramid_registry is not None
            and isinstance(orig_pyramid_registry, Registry)
            else get_original_app_or_fail(wsgi_app, Registry)
        )

        app_name = self._get_app_name()
        super().__init__(wsgi_app, app_name)

    @fail_quietly(
        "Unable to get Pyramid application name", return_value="Pyramid Application"
    )
    def _get_app_name(self):
        return self.registry.package_name
