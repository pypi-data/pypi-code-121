"""
Core API functions to communicate with the Projectal server.

Get the `status()` of the Projectal server, run a `query()`,
or make custom HTTP requests to any Projectal API method.

**Verb functions (GET, POST, etc.)**

The HTTP verb functions provided here are used internally by
this library; in general, you should not need to use these
functions directly unless this library's implementation of
an API method is insufficient for your needs.

The response is validated automatically for all verbs. A
`projectal.errors.ProjectalException` is thrown if the response
fails, otherwise you get a `dict` containing the JSON response.

**Login and session state**

This module handles logins and session state for the library.
It's done for you automatically by the module when you make the
first authenticated request. See `login()` for details.
"""
from datetime import timezone, datetime

import requests
from packaging import version

try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json.decoder import JSONDecodeError

from .errors import *
import projectal


def status():
    """Get runtime details of the Projectal server (with version number)."""
    _check_creds_or_fail()
    response = requests.get(projectal.api_base + '/management/status')
    return response.json()


def _check_creds_or_fail():
    """Correctness check: can't proceed if no API details supplied."""
    if not projectal.api_base:
        raise LoginException('Projectal URL is not set')
    if not projectal.api_username or not projectal.api_password:
        raise LoginException('API credentials are missing')


def _check_version_or_fail():
    """
    Check the version number of the Projectal instance. If the
    version number is below the minimum supported version number
    of this API client, raise a ProjectalVersionException.
    """
    v = projectal.status()['version']
    min = projectal.MIN_PROJECTAL_VERSION
    if version.parse(v) >= version.parse(min):
        return True
    m = "Minimum supported Projectal version: {}. Got: {}".format(min, v)
    raise ProjectalVersionException(m)


def login():
    """
    Log in using the credentials supplied to the module. If successful,
    stores the cookie in memory for reuse in future requests.

    **You do not need to manually call this method** to use this library.
    The library will automatically log in before the first request is
    made or if the previous session has expired.

    This method can be used to check if the account credentials are
    working correctly.
    """
    _check_version_or_fail()

    payload = {
        'username': projectal.api_username,
        'password': projectal.api_password
    }
    if projectal.api_application_id:
        payload['applicationId'] = projectal.api_application_id
    response = requests.post(projectal.api_base + '/auth/login', json=payload)
    # Handle errors here
    if response.status_code == 200 and response.json()['status'] == 'OK':
        projectal.cookies = response.cookies
        return True
    raise LoginException('Check the API URL and your credentials')


def auth_details():
    """
    Returns some details about the currently logged-in user account,
    including all permissions available to it.
    """
    return projectal.get('/api/user/details')


def permission_list():
    """
    Returns a list of all permissions that exist in Projectal.
    """
    return projectal.get('/api/permission/list')


def query(payload):
    """
    Executes a query and returns the result. See the
    [Query API](https://projectal.com/docs/latest#tag/Query) for details.
    """
    return projectal.post('/api/query/match', payload)


def date_from_timestamp(date):
    """Returns a date string from a timestamp.
    E.g., `1647561600000` returns `2022-03-18`."""
    return str(datetime.utcfromtimestamp(int(date)/1000).date())


def timestamp_from_date(date):
    """Returns a timestamp from a date string.
    E.g., `2022-03-18` returns `1647561600000`."""
    return int(datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)

def timestamp_from_datetime(date):
    """Retuns a timestamp from a datetime string.
    E.g. `2022-03-18 17:00` returns `1647622800000`."""
    return int(datetime.strptime(date, "%Y-%m-%d %H:%M")
               .replace(tzinfo=timezone.utc).timestamp() * 1000)

def post(endpoint, payload=None, file=None, is_json=True):
    """HTTP POST to the Projectal server."""
    return __request('post', endpoint, payload, file=file, is_json=is_json)


def get(endpoint, payload=None, is_json=True):
    """HTTP GET to the Projectal server."""
    return __request('get', endpoint, payload, is_json=is_json)


def delete(endpoint, payload=None):
    """HTTP DELETE to the Projectal server."""
    return __request('delete', endpoint, payload)


def put(endpoint, payload=None, file=None, form=False):
    """HTTP PUT to the Projectal server."""
    return __request(
        'put', endpoint, payload, file=file, form=form)


def __request(method, endpoint, payload=None, file=None, form=False, is_json=True):
    """
    Make an API request. If this is the first request made in the module,
    this function will issue a login API call first.

    Additionally, if the response claims an expired JWT, the function
    will issue a login API call and try the request again (max 1 try).
    """
    if not projectal.cookies:
        projectal.login()
    fun = getattr(requests, method)
    kwargs = {}
    if file:
        kwargs['files'] = file
        kwargs['data'] = payload
    elif form:
        kwargs['data'] = payload
    else:
        kwargs['json'] = payload
    response = fun(projectal.api_base + endpoint, cookies=projectal.cookies, **kwargs)

    try:
        # Raise error for non-200 response
        response.raise_for_status()
    except HTTPError:
        # If the error is from an expired JWT we can retry it by
        # clearing the cookie. (Login happens on next call).
        try:
            r = response.json()
            if (r.get('status', None) == 'UNAUTHORIZED'
                    or r.get('message', None) == 'anonymousUser'
                    or r.get('error', None) == 'Unauthorized'):
                projectal.cookies = None
                return __request(method, endpoint, payload, file)
        except JSONDecodeError:
            pass
        raise ProjectalException(response) from None

    # We will treat a partial success as failure - we cannot silently
    # ignore some errors
    if response.status_code == 207:
        raise ProjectalException(response)

    if not is_json:
        return response
    try:
        payload = response.json()
        # Fail if the status code in the response body (not the HTTP code!)
        # does not match what we expect for the API endpoint.
        __maybe_fail_status(response, payload)
        # If we have a timestamp, record it for whoever is interested
        if 'timestamp' in payload:
            projectal.response_timestamp = payload['timestamp']
        else:
            projectal.response_timestamp = None

        # If we have a 'jobCase', return the data it points to, which is
        # what the caller is after (saves them having to do it every time).
        if 'jobCase' in payload:
            return payload[payload['jobCase']]
        return payload
    except JSONDecodeError:
        # API always responds with JSON. If not, it's an error
        raise ProjectalException(response) from None


def __maybe_fail_status(response, payload):
    """
    Check the status code in the body of the response. Raise
    a `ProjectalException` if it does not match the "good"
    status for that request.

    The code is "OK" for everything, but /create returns "CREATED".
    Luckily for us, /create also returns a 201, so we know which
    codes to match up.

    Requests with no 'status' key are assumed to be good.
    """
    expected = "OK"
    if response.status_code == 201:
        expected = "CREATED"

    got = payload.get('status', expected)
    if expected == got:
        return True
    m = "Unexpected response calling {}. Expected status: {}. Got: {}". \
        format(response.url, expected, got)
    raise ProjectalException(response, m)
