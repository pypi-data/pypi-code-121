"""Send HTTP requests to CMEM API."""
import json

import requests

from . import config


def get_access_token(_oauth_token_uri=None, _oauth_credentials=None):
    """Return access token string.

    This is a wrapper for get_token to get only the string.
    It does NOT fetch a new token in case a 'prefetched_token" grant type.
    """
    if config.get_oauth_grant_type() == "prefetched_token":
        return config.get_oauth_access_token()
    return get_token(_oauth_token_uri, _oauth_credentials)["access_token"]


def get_token(_oauth_token_uri=None,
              _oauth_credentials=None):
    """
    Return auth token json structure.

    Auth token format is:
    {
        'token_type': 'bearer',
        'refresh_token': '923a28d6-470d-4afd-9b91-0c952a29a423',
        'expires_in': 43199,
        'access_token': '55c21f4e-9529-4399-aaf1-128acb9da4a1',
        'scope': 'read'
    }
    """
    if not _oauth_credentials:
        _oauth_credentials = config.get_oauth_default_credentials()
    if not _oauth_token_uri:
        _oauth_token_uri = config.get_oauth_token_uri()
    post_req = _request(
        'post',
        _oauth_token_uri,
        data=_oauth_credentials
    )
    post_req.raise_for_status()
    response = post_req.content.decode("utf-8")
    try:
        parsed_json = json.loads(response)
    except json.decoder.JSONDecodeError:
        # pylint: disable=raise-missing-from
        raise ValueError(
            "Token response is not proper JSON. Response was:\n{}"
            .format(response)
        )
    return parsed_json


# pylint: disable-msg=too-many-arguments
def send_request(uri, method="GET", data=None,
                 _json=None, headers=None, params=None,
                 files=None):
    """Return HTML content for request directly."""
    return request(uri, method=method, data=data,
                   _json=_json, headers=headers, params=params,
                   files=files).content


# pylint: disable-msg=too-many-arguments
def get_json(uri, method="GET", data=None, _json=None,
             headers=None, params=None, files=None):
    """Return parsed JSON content for request directly."""
    response = request(uri, method=method, data=data, _json=_json,
                       headers=headers, params=params, files=files).content
    return json.loads(response.decode("utf-8"))


def _request(method=None, url=None, **kwargs):
    return requests.api.request(
        method,
        url,
        verify=config.get_ssl_verify(),
        **kwargs
    )


# pylint: disable-msg=too-many-arguments
def request(uri, method="GET", data=None,
            _json=None, headers=None, params=None,
            files=None, stream=False):
    """Return raw response object."""
    if headers is None:
        headers = {}
    headers['Authorization'] = "Bearer {}".format(str(get_access_token()))
    headers['User-Agent'] = config.get_cmem_user_agent()
    if method == "GET":
        response = _request(
            'get',
            uri,
            headers=headers,
            stream=stream,
            params=params
        )
    elif method == "POST":
        response = _request(
            'post',
            uri,
            headers=headers,
            data=data,
            params=params,
            files=files,
            stream=stream
        )
    elif method == "PUT":
        if config.is_chatty():
            print(headers)
        response = _request(
            'put',
            uri,
            headers=headers,
            data=data,
            params=params,
            files=files,
            stream=stream
        )
    elif method == "DELETE":
        response = _request(
            'delete',
            uri,
            headers=headers,
            params=params,
            stream=stream
        )
    elif method == "PATCH":
        response = _request(
            'patch',
            uri,
            headers=headers,
            data=data,
            params=params,
            files=files,
            stream=stream
        )
    else:
        raise Exception("Unknown HTTP request method")
    if response.status_code not in [requests.status_codes.codes.ok,
                                    requests.status_codes.codes.no_content,
                                    requests.status_codes.codes.created]:
        if config.is_chatty():
            print("Request failed for URL: {} {}".format(
                response.url, response.request.method))
            print(response.content.decode("utf-8"))
            print(response.status_code)
    response.raise_for_status()
    return response
