# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
class WrongDjangoMiddlewareException(RuntimeError):
    MSG_FMT = (
        "Incorrect Contrast middleware.\n"
        "You are likely using settings.{setting}, which requires Contrast's {type} DjangoMiddleware.\n"
        "Please use '{middleware}' in settings.{setting}."
    )

    """
    Error message if we see that the application _should_ be using the legacy middleware,
    but is actually using the standard middleware.
    """
    USE_LEGACY_MSG = MSG_FMT.format(
        setting="MIDDLEWARE_CLASSES",
        type="legacy",
        middleware="contrast.agent.middlewares.legacy_django_middleware.DjangoMiddleware",
    )

    """
    Error message if we see that the application _should_ be using the standard middleware,
    but is actually using the legacy middleware
    """
    USE_STANDARD_MSG = MSG_FMT.format(
        setting="MIDDLEWARE",
        type="standard",
        middleware="contrast.agent.middlewares.django_middleware.DjangoMiddleware",
    )

    def __init__(self, using_legacy_middleware):
        # since we don't see our middleware in the expected setting, assume that they are using the other setting
        msg = self.USE_STANDARD_MSG if using_legacy_middleware else self.USE_LEGACY_MSG
        RuntimeError.__init__(self, msg)
