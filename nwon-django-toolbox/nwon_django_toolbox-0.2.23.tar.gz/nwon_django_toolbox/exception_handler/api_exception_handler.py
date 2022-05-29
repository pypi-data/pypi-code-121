from typing import Any, Dict, Optional

from rest_framework.response import Response
from rest_framework.views import exception_handler

from nwon_django_toolbox.exception_handler.get_error_response import get_error_response


def api_exception_handler(
    exc: Exception, context: Dict[str, Any]
) -> Optional[Response]:
    """Custom API exception handler."""

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:

        response.data = get_error_response(
            status_code=response.status_code,
            details=response.data,
        )

    return response
