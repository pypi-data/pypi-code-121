from collections import defaultdict

from argus_api.exceptions.http import (
    ArgusException,
    AuthenticationFailedException,
    AccessDeniedException,
    ObjectNotFoundException,
    ValidationErrorException,
    ServiceUnavailableException,
)


status_exceptions = defaultdict(
    lambda: ArgusException,
    {
        401: AuthenticationFailedException,
        403: AccessDeniedException,
        404: ObjectNotFoundException,
        412: ValidationErrorException,
        503: ServiceUnavailableException,
    },
)


def validate_http_response(resp):
    """Handling status codes in HTML responses

    :param resp: response with status code attribute
    """

    try:
        if resp.status_code >= 400:
            raise status_exceptions[resp.status_code](resp)

    except AttributeError:
        msg = (
            "The provided object is not a requests.Response-like object:\n"
            f"Object: {resp}"
        )
        raise ValueError(msg)
