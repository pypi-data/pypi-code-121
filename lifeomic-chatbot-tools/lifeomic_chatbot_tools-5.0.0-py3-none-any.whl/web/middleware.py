import typing as t

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.routing import APIRoute
from loguru import logger as _logger
from starlette.exceptions import HTTPException as StarletteHTTPException


def _make_error_logging_route_handler_class(*, msg_prefix="", logger) -> t.Type[APIRoute]:
    """
    Makes a FastAPI route handler class which intercepts and logs all internal errors that occur in a FastAPI app.
    Related docs: https://fastapi.tiangolo.com/advanced/custom-request-and-route/
    """

    class ErrorLoggingRouteHandler(APIRoute):
        def get_route_handler(self) -> t.Callable:
            original_route_handler = super().get_route_handler()

            async def custom_route_handler(request: Request) -> Response:
                try:
                    # Try to handle the route as normal.
                    return await original_route_handler(request)
                except Exception as exc:
                    # Some type of exception has occurred. If it's a normal Python exception or a 500-level exception,
                    # log it here.
                    error_to_report = None
                    is_fastapi_error = isinstance(exc, (StarletteHTTPException, RequestValidationError))
                    if not is_fastapi_error:
                        # This is an unknown internal exception.
                        error_to_report = msg_prefix + str(exc)

                    if isinstance(exc, StarletteHTTPException) and exc.status_code >= 500:
                        # This is a 500-level internal exception.
                        error_to_report = msg_prefix + exc.detail

                    if error_to_report is not None:
                        # Log the error.
                        logger.exception(error_to_report)

                    if is_fastapi_error:
                        # FastAPI has a native way for handling these types of errors, so we'll let it bubble up to
                        # those handlers.
                        raise exc
                    else:
                        # Turn the normal Python exception into an HTTP exception with a message for the caller.
                        # This is the error FastAPI will return to the user.
                        server_response = "An internal error has occurred. Our team has been notified of this incident."
                        raise HTTPException(500, server_response)

            return custom_route_handler

    return ErrorLoggingRouteHandler


def with_error_logging(app: FastAPI, msg_prefix="", logger=_logger):
    """
    Adds middleware to ``app`` which intercepts and logs all internal errors that occur in the app. Intercepts all
    ``Exception`` objects which are uncaught by the app, as well as all 500-level errors intentionally thrown by the
    app.

    Parameters
    ----------
    app : FastAPI
        The FastAPI app to add the middleware to.
    msg_prefix : str, optional
        If provided, this string will be pre-pended to the error messages of all intercepted errors before they are
        logged and reported.
    logger : object, optional
        logger to call when generating log lines. Defaults to the default loguru logger. Must have an ``exception``
        method that can be called e.g. ``logger.exception("error")``.
    """
    app.router.route_class = _make_error_logging_route_handler_class(msg_prefix=msg_prefix, logger=logger)
    return app
