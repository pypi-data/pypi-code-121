from requests import request

from api_manager.constants import Project
from api_manager.exceptions import NotConfiguredException
from api_manager.headers import HeadersTemplates, PROJECT_HEADERS
from api_manager.logger import logging_response


def basic_request(
        method: str,
        url: str,
        user: dict = None,
        with_auth: bool = True,
        headers_type: HeadersTemplates = HeadersTemplates.DEFAULT,
        project: Project = None,
        **kwargs
):
    """
    :param method: Http method, like GET, POST, PUT, PATCH, DELETE
    :param url: Endpoint url
    :param project:
    :param user: user which should be used for getting ``Bearer`` token.
    If user is None then by default ``DEFAULT_USER`` is used. If you want to
    use other user, then provide credentials as:
    {
        "username": <some_email>,
        "password": <some_password>,
        "client_id": "insomnia",
        "client_secret": "insomnia",
        "grant_type": "password"
    }
    :param with_auth: FLag that declare should we use authentication headers for request either not.
    If set to True, then request will have header like:
    {'Authorization': 'Bearer <some_token>'}
    :param headers_type: Headers type which should be used for request. We need this because,
    some of requests should have for example {'Content-type': 'application/json'}, but
    others do not need any headers.

    All available headers can be viewed in ``HeadersTemplates``. If you want to add your
    custom headers, then add new headers to ``HeadersTemplates``, and pass it inside
    method like this:
    post(<url>, data={}, headers_type=HeadersTemplates.MY_CUSTOM)

    :param kwargs: additional params
    :return: :class:`Response <Response>` object

    This method has included logger, if you want to stop seeing API logs,
    then in settings.py set ``REQUESTS_LOGGING`` to False.

    ``Verify`` property by default set in setting.py ``CERT_PATH``. We need
    this property because if not set, then we will unable to make request.
    If set to False, then we will get insecure warning, but if set to
    some cert path, then no warnings and no errors.
    """
    from api_manager.settings import PROJECT, CERT_PATH

    safe_project = project or PROJECT

    if safe_project is None:
        raise NotConfiguredException(
            'You should define "PROJECT" setting in your settings file.'
            'Or provide "project" attribute to your method'
        )

    kwargs.setdefault('headers', PROJECT_HEADERS[safe_project](user, with_auth, headers_type))
    if CERT_PATH:
        kwargs.setdefault('verify', CERT_PATH)

    response = request(method, url, **kwargs)
    logging_response(response)

    return response


def get(url, params=None, user=None, **kwargs):
    """
    Sends a GET request.

    :param user: user to get token
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return basic_request('get', url, user=user, params=params, **kwargs)


def post(url, json=None, user=None, **kwargs):
    """
    Sends a POST request.

    :param user: user to get token
    :param url: URL for the new :class:`Request` object.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return basic_request('post', url, user=user, json=json, **kwargs)


def put(url, json=None, user=None, **kwargs):
    """
    Sends a PUT request.

    :param user: user to get token
    :param url: URL for the new :class:`Request` object.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return basic_request('put', url, user=user, json=json, **kwargs)


def patch(url, json=None, user=None, **kwargs):
    """
    Sends a PATCH request.

    :param user: user to get token
    :param url: URL for the new :class:`Request` object.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return basic_request('patch', url, user=user, json=json, **kwargs)


def delete(url, user=None, **kwargs):
    """
    Sends a DELETE request.

    :param user: user to get token
    :param url: URL for the new :class:`Request` object.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return basic_request('delete', url, user=user, **kwargs)
