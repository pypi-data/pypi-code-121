# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os
import sys

from contrast.agent.assess.rules.config import (
    DjangoHttpOnlyRule,
    DjangoSecureFlagRule,
    DjangoSessionAgeRule,
)

from contrast.wsgi.middleware import WSGIMiddleware
from contrast.agent.middlewares.route_coverage.django_routes import (
    create_django_routes,
    build_django_route,
)
from contrast.utils.decorators import fail_quietly

try:
    from django.urls import get_resolver
except ImportError:
    from django.core.urlresolvers import get_resolver

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class DjangoWSGIMiddleware(WSGIMiddleware):
    """
    A subclass of the WSGI middleware that provides django route coverage and config
    scanning.

    This is not a Django-style middleware - it must wrap django's WSGI_APPLICATION,
    and does not belong in MIDDLEWARE / MIDDLEWARE_CLASSES.
    """

    def __init__(self, wsgi_app):
        self.app_name = self.get_app_name()

        self.config_rules = [
            DjangoSessionAgeRule(),
            DjangoSecureFlagRule(),
            DjangoHttpOnlyRule(),
        ]

        super().__init__(wsgi_app, self.app_name)

    @fail_quietly(
        "Unable to get Django application name", return_value="Django Application"
    )
    def get_app_name(self):
        from django.conf import settings

        wsgi_application = settings.WSGI_APPLICATION

        return wsgi_application.split(".")[0]

    @fail_quietly("Unable to get Django view func")
    def get_view_func(self, request):
        from django.conf import settings

        match = self._run_router(self.request_path)
        if (
            match is None
            and not self.request_path.endswith("/")
            and "django.middleware.common.CommonMiddleware" in settings.MIDDLEWARE
            and settings.APPEND_SLASH
        ):
            match = self._run_router(f"{self.request_path}/")
        if match is None:
            return None

        return match.func

    @fail_quietly("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return build_django_route(view_func)

    @fail_quietly("Unable to get route coverage", return_value={})
    def get_route_coverage(self):
        """
        Route Coverage is the Assess feature that looks for routes generally defined
        in Django apps in a file like urls.py
        """
        return create_django_routes()

    @fail_quietly("Failed to run config scanning rules")
    def _scan_configs(self):
        """
        Run config scanning rules for assess

        Overridden from base class; gets called from base class
        """
        from django.conf import settings as app_settings

        app_config_module_name = os.environ.get("DJANGO_SETTINGS_MODULE")
        if not app_config_module_name:
            logger.warning("Unable to find Django settings for config scanning")
            return

        app_config_module = sys.modules.get(app_config_module_name)
        if not app_config_module:
            logger.warning("Django settings module not loaded; can't scan config")
            return

        for rule in self.config_rules:
            rule.apply(app_settings, app_config_module)

    @fail_quietly("Failed to _run_router for django middleware")
    def _run_router(self, path):
        return get_resolver().resolve(path or "/")
