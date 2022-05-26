# encoding: utf-8
from __future__ import absolute_import

import enum
from platform import python_implementation, python_version
from time import sleep

import requests
from requests.exceptions import RequestException

import rapyuta_io
from rapyuta_io.utils import APIError

DEFAULT_RETRY_COUNT = 4
WAIT_TIME_IN_SEC = 1


requests.utils.default_user_agent = lambda: 'rapyuta_io/{} {}/{} python-requests/{}'.format(
    rapyuta_io.__version__, python_implementation(), python_version(), requests.__version__)


class HttpMethod(str, enum.Enum):

    def __str__(self):
        return str(self.value)

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'


class RestClient:
    def __init__(self, url):
        self._url = url
        self._retry_limit = DEFAULT_RETRY_COUNT
        self._retry_count = 0
        self._method = HttpMethod.GET.value
        self._headers = {}
        self._query_params = {}

    def url(self, url):
        self._url = url
        return self

    def method(self, http_method):
        self._method = http_method.value
        return self

    def headers(self, headers):
        self._headers = headers
        return self

    def retry(self, retry_limit):
        if type(retry_limit) is int:
            self._retry_limit = retry_limit
        return self

    def query_param(self, query_param):
        self._query_params = query_param
        return self

    def _request(self, payload, raw=False):
        kwargs = {'method': self._method, 'url': self._url,
                  'headers': self._headers, 'params': self._query_params}
        if raw:
            response = requests.request(data=payload, **kwargs)
            return response
        response = requests.request(json=payload, **kwargs)
        return response

    def execute(self, payload=None, raw=False):
        while True:
            try:
                # It will not be respecting the Retry Limit, when the server
                # returns Internal Server Error (500) for a GET Request. This is
                # because in most places of the SDK we are setting Retry Limit
                # explicitly to 0. The plan is to deprecate the Retry Limit in
                # future.
                response = self._request(payload, raw)
                if self._method != HttpMethod.GET.value or \
                        response.status_code != requests.codes.INTERNAL_SERVER_ERROR or \
                        self._retry_count >= DEFAULT_RETRY_COUNT:
                    return response
            except RequestException as err:
                if self._retry_count >= self._retry_limit:
                    raise APIError("Error occurred for URL {}: {}".format(self._url, err))

            sleep(WAIT_TIME_IN_SEC)
            self._retry_count += 1
