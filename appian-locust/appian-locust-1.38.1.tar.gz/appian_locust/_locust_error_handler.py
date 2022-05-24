import inspect
import os
from functools import wraps
from typing import Any, Callable, Optional

from locust.clients import ResponseContextManager
from requests.exceptions import HTTPError
from requests.models import Response

from appian_locust.helper import ENV

from . import logger

log = logger.getLogger(__name__)


def _format_http_error(resp: Response, uri: str, username: str) -> str:
    """Taken from Response.raise_for_status. Formats the http error message,
     additionally adding the username

    Args:
        resp (Response): Response to generate an http error message from
        uri (str): URI accessed as part of the request
        username (str): Username of the calling user

    Returns:
        str: the http error message to use
    """
    http_error_msg = ''
    if isinstance(resp.reason, bytes):
        # We attempt to decode utf-8 first because some servers
        # choose to localize their reason strings. If the string
        # isn't utf-8, we fall back to iso-8859-1 for all other
        # encodings. (See PR #3538)
        try:
            reason = resp.reason.decode('utf-8')
        except UnicodeDecodeError:
            reason = resp.reason.decode('iso-8859-1')
    else:
        reason = resp.reason

    if 400 <= resp.status_code < 500:
        http_error_msg = u'%s Client Error: %s for uri: %s Username: %s' % (resp.status_code, reason, uri, username)

    elif 500 <= resp.status_code < 600:
        http_error_msg = u'%s Server Error: %s for uri: %s Username: %s' % (resp.status_code, reason, uri, username)

    return http_error_msg


def test_response_for_error(resp: ResponseContextManager, uri: str = 'No URI Specified', raise_error: bool = True, username: str = "") -> None:
    """
    Locust relies on errors to be logged to the global_stats attribute for error handling.
    This function is used to notify Locust that its instances are failing and that it should fail too.

    Args:
        resp (Response): a python response object from a client.get() or client.post() call in Locust tests.
        uri (Str): URI in the request that caused the above response.
        username (Str): identifies the current user when we use multiple different users for locust test)

    Returns:
        None

    Example (Returns a HTTP 500 error):

    .. code-block:: python
      username = 'admin'
      uri = 'https://httpbin.org/status/500'
      with self.client.get(uri) as resp:
        test_response_for_error(resp, uri, username)
    """
    try:
        if not resp or not resp.ok:
            http_error_msg = _format_http_error(resp, uri, username)
            error = HTTPError(http_error_msg)
            resp.failure(error)
            # TODO: Consider using this resp.failure construct in other parts of the code
            log_locust_error(
                error,
                'REQUEST:',
                f'URI: {resp.url}',
                raise_error=raise_error
            )
    except HTTPError as e:
        raise e
    except Exception as e:
        log_locust_error(
            Exception(f'MESSAGE: {e}'),
            'REQUEST:',
            f'URI: {resp.url}',
            raise_error=True
        )


def log_locust_error(e: Exception, error_desc: str = 'No description', location: Optional[str] = None, raise_error: bool = True) -> None:
    """
    This function allows scripts in appian_locust to manually report an error to locust.

    Args:
        e (Exception): whichever error occured should be propagated through this variable.
        error_desc (str): contains information about the error.
        location (str): Codepath or URL path for the error. If non specified, this will become the codepath
        raise_error (bool): Whether or not to raise the exception

    Returns:
        None

    Example:

    .. code-block:: python

        if not current_news:
            e = Exception(f"News object: {current} news does not exist.")
            desc = f'Error in get_news function'
            log_locust_error(e, error_desc=desc)
    """
    if not location:
        # Infer location from inspecting the frame
        if len(inspect.stack()) > 1:
            stack_item: inspect.FrameInfo = inspect.stack()[1]
            file_without_path = os.path.basename(stack_item.filename)
            location = f'{file_without_path}/{stack_item.function}()'
    ENV.stats.log_error(f'DESC: {error_desc}', f'LOCATION: {location}', f'EXCEPTION: {e}')

    if raise_error:
        raise e


def raises_locust_error(func: Callable) -> Callable:
    """Indicates that the below method should log a locust error

    Args:
        func (Callable): method that could throw an exception

    Returns:
        Callable: a wrapped form of that method
    """
    @wraps(func)
    def func_wrapper(*args: Any, **kwargs: Any) -> Optional[Callable]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            file_without_path = os.path.basename(inspect.getfile(func))
            location = f'{file_without_path}/{func.__name__}()'
            log_locust_error(e, location=location, raise_error=True)
            return None
    return func_wrapper
