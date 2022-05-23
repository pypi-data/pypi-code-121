try:
    from simplejson import JSONDecodeError
except ImportError:
    from json import JSONDecodeError


from requests import Response
import logging


log = logging.getLogger(__name__)


def _format_error(e):
    """Formats an Argus error message

    {
        "type": "ACTION_ERROR",
        "field": None,
        "message": "Something went wrong",
        "parameter": ...
    }

    into a single string to show as an error message at run-time
    :param e:
    :return:
    """

    if e["type"] == "FIELD_ERROR":
        return f"{e['type']} ({e['field']}): {e['message']}"
    else:
        return f"{e['type']}: {e['message']}"


class ArgusException(Exception):
    def __init__(self, resp):
        if isinstance(resp, Response):
            try:
                parsed_resp = resp.json()
            except JSONDecodeError:
                # response content is not JSON, which is suspicious because
                # error responses are in JSON format
                parsed_resp = resp
        else:
            parsed_resp = resp

        if "messages" in parsed_resp:
            message_body = "\n".join(
                [_format_error(msg) for msg in parsed_resp["messages"]]
            )
        else:
            message_body = str(parsed_resp)

        if hasattr(resp, "reason") and hasattr(resp, "status_code"):
            self.status_code = resp.status_code
            self.message = (
                f"Status code {resp.status_code}: " f"{resp.reason}\n{message_body} "
            )
        else:
            self.message = message_body

        self.parsed_resp = parsed_resp
        super().__init__(self.message)


class AuthenticationFailedException(ArgusException):
    """Used for HTTP 401"""

    pass


class AccessDeniedException(ArgusException):
    """Used for HTTP 403"""

    pass


class ObjectNotFoundException(ArgusException):
    """Used for HTTP 404"""

    pass


class ValidationErrorException(ArgusException):
    """Used for HTTP 412"""

    pass


class ServiceUnavailableException(ArgusException):
    """Used for HTTP 503"""

    pass


class MultipleValidationErrorException(Exception):
    pass
