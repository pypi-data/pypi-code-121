# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.utils.object_utils import get_name
from contrast.utils.decorators import fail_loudly

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


def get_original_app_or_fail(app, orig_app_class):
    _app = find_original_application(app, orig_app_class)
    if isinstance(_app, orig_app_class):
        return _app

    msg = (
        f"Unable to find the original {get_name(orig_app_class)} Application object. "
        f"Please provide the original {get_name(orig_app_class)} Application object as the second argument to "
        "ContrastMiddleware."
    )

    logger.error(msg)
    raise RuntimeError(msg)


@fail_loudly("Unable to find original application object")
def find_original_application(app, orig_app_class, depth=20):
    """
    Recursively search through the middleware chain of `app` for an
    application of type `orig_app_class`. Most WSGI/ASGI middlewares are implemented as
    classes and maintain a reference to their wrapped app as an attribute. This function
    makes a best effort to find this attribute on each successive middleware until it
    sees an instance of the desired class.

    This method is not intended to succeed every time, as it is based off of several
    assumptions that will not always be true. It needs only succeed often enough that
    customers rarely need to supply additional information to framework-specific
    middleware constructors.

    This delegates to _find_original_application to ensure that we don't get an extra
    @fail_loudly on each recursive call.
    """
    return _find_original_application(app, orig_app_class, depth)


def _find_original_application(app, orig_app_class, depth):
    if isinstance(app, orig_app_class):
        return app
    if depth == 0:
        return None

    # this list is in approximate order of expected app attribute name; since this
    # algorithm is greedy, we iterate over the best candidates first
    for attr_name in [
        "app",
        "application",
        "wsgi_app",
        "asgi_app",
        "_app",
        "_wsgi_app",
        "_asgi_app",
        "_application",
        "wsgi_application",
        "asgi_application",
        "_wsgi_application",
        "_asgi_application",
        "wrapped_app",
        "wrapped_application",
        "wrapped",
        "wrap_app",
        "wrap",
        "registry",  # pyramid
        "_wrapped",
        "_wrapped_app",
        "_wrapped_application",
        "_wrap_app",
        "_wrap",
    ]:
        attr = getattr(app, attr_name, None)

        # The name check is a very unfortunate thing we have to do since
        # Pyramid's Registry obj is not a callable.
        if callable(attr) or attr.__class__.__name__ == "Registry":
            return _find_original_application(attr, orig_app_class, depth - 1)

    return None
