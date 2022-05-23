import json
import requests
from time import sleep
from random import randint
from datetime import datetime
from marshmallow import Schema

from .exceptions import PriceCypherError, RateLimitError

UNKNOWN_ERROR = 'pricecypher.sdk.internal.unknown'


class RestClientOptions(object):
    """
    Configuration object for RestClient.
    Used for configuring additional RestClient options, such as rate-limit retries.

    :param float or tuple[float,float] timeout: (optional) Change the requests connect and read timeout (in seconds).
        Pass a tuple to specify both values separately or a float to set both to it.
        (defaults to 300.0 (5 minutes) for both)
    :param int retries: (optional) In the event an API request returns a 429 response header (indicating rate-limit
        has been hit), the RestClient will retry the request this many times using an exponential backoff strategy,
        before raising a RateLimitError exception.
        (defaults to 3)
    """

    def __init__(self, timeout=None, retries=None):
        self.timeout = 300.0
        self.retries = 3

        if timeout is not None:
            self.timeout = timeout

        if retries is not None:
            self.retries = retries


class RestClient(object):
    """
    Provides simple methods for handling all RESTful api endpoints.

    :param str jwt: JWT token used to authorize requests to the APIs.
    :param RestClientOptions options: (optional) Pass an instance of RestClientOptions to configure additional
        RestClient options, such as rate-limit retries.
    """

    def __init__(self, jwt, options=None):
        if options is None:
            options = RestClientOptions()

        self.options = options
        self.jwt = jwt

        self._metrics = {'retries': 0, 'backoff': []}
        self._skip_sleep = False

        self.base_headers = {
            'Authorization': 'Bearer {}'.format(self.jwt),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    # Returns the maximum amount of jitter to introduce in milliseconds (100ms)
    def MAX_REQUEST_RETRY_JITTER(self):
        return 100

    # Returns the maximum delay window allowed (1000ms)
    def MAX_REQUEST_RETRY_DELAY(self):
        return 1000

    # Returns the minimum delay window allowed (100ms)
    def MIN_REQUEST_RETRY_DELAY(self):
        return 100

    def _retry(self, make_request):
        # Track the API request attempt number
        attempt = 0

        # Reset the metrics tracker
        self._metrics = {'retries': 0, 'backoff': []}

        # Floor the retries at 0.
        retries = max(0, self.options.retries)

        while True:
            # Increment attempt number
            attempt += 1

            # Issue the request
            response = make_request()

            # break iff no retry needed
            if response.status_code != 429 or retries <= 0 or attempt > retries:
                break

            # Retry the request. Apply an exponential backoff for subsequent attempts, using this formula:
            # max(
            #   MIN_REQUEST_RETRY_DELAY,
            #   min(MAX_REQUEST_RETRY_DELAY, (100ms * (2 ** attempt - 1)) + random_between(1, MAX_REQUEST_RETRY_JITTER))
            # )

            # Increases base delay by (100ms * (2 ** attempt - 1))
            wait = 100 * 2 ** (attempt - 1)

            # Introduces jitter to the base delay; increases delay between 1ms to MAX_REQUEST_RETRY_JITTER (100ms)
            wait += randint(1, self.MAX_REQUEST_RETRY_JITTER())

            # Is never more than MAX_REQUEST_RETRY_DELAY (1s)
            wait = min(self.MAX_REQUEST_RETRY_DELAY(), wait)

            # Is never less than MIN_REQUEST_RETRY_DELAY (100ms)
            wait = max(self.MIN_REQUEST_RETRY_DELAY(), wait)

            self._metrics['retries'] = attempt
            self._metrics['backoff'].append(wait)

            # Skip calling sleep() when running unit tests
            if self._skip_sleep is False:
                # sleep() functions in seconds, so convert the milliseconds formula above accordingly
                sleep(wait / 1000)

        # Return the final Response
        return response

    def get(self, url, params=None, schema: Schema = None):
        headers = self.base_headers.copy()
        response = self._retry(lambda: requests.get(url, params=params, headers=headers, timeout=self.options.timeout))

        return self._process_response(response, schema)

    def post(self, url, data=None, schema: Schema = None):
        headers = self.base_headers.copy()
        j_data = json.dumps(data, cls=JsonEncoder)
        response = self._retry(lambda: requests.post(url, data=j_data, headers=headers, timeout=self.options.timeout))

        return self._process_response(response, schema)

    def file_post(self, url, data=None, files=None):
        headers = self.base_headers.copy()
        headers.pop('Content-Type', None)

        response = self._retry(
            lambda: requests.post(url, data=data, files=files, headers=headers, timeout=self.options.timeout))
        return self._process_response(response)

    def patch(self, url, data=None):
        headers = self.base_headers.copy()

        response = self._retry(lambda: requests.patch(url, json=data, headers=headers, timeout=self.options.timeout))
        return self._process_response(response)

    def put(self, url, data=None):
        headers = self.base_headers.copy()

        response = self._retry(lambda: requests.put(url, json=data, headers=headers, timeout=self.options.timeout))
        return self._process_response(response)

    def delete(self, url, params=None, data=None):
        headers = self.base_headers.copy()

        response = self._retry(
            lambda: requests.delete(url, headers=headers, params=params or {}, json=data, timeout=self.options.timeout))
        return self._process_response(response)

    def _process_response(self, response, schema=None):
        return self._parse(response, schema).content()

    def _parse(self, response, schema=None):
        if not response.text:
            return EmptyResponse(response.status_code)
        try:
            return JsonResponse(response, schema)
        except ValueError:
            return PlainResponse(response)


class Response(object):
    def __init__(self, status_code, content, headers):
        self._status_code = status_code
        self._content = content
        self._headers = headers

    def content(self):
        if self._is_error():
            if self._status_code == 429:
                reset_at = int(self._headers.get('x-ratelimit-reset', '-1'))
                raise RateLimitError(error_code=self._error_code(),
                                     message=self._error_message(),
                                     reset_at=reset_at)

            raise PriceCypherError(status_code=self._status_code,
                                   error_code=self._error_code(),
                                   message=self._error_message())
        else:
            return self._content

    def _is_error(self):
        return self._status_code is None or self._status_code >= 400

    # Force implementation in subclasses
    def _error_code(self):
        raise NotImplementedError

    def _error_message(self):
        raise NotImplementedError


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class JsonResponse(Response):
    def __init__(self, response, schema: Schema = None):
        if schema is not None and response.status_code < 400:
            content = schema.loads(json_data=response.text)
        else:
            content = json.loads(response.text)
        super(JsonResponse, self).__init__(response.status_code, content, response.headers)

    def _error_code(self):
        if 'errorCode' in self._content:
            return self._content.get('errorCode')
        elif 'error' in self._content:
            return self._content.get('error')
        else:
            return UNKNOWN_ERROR

    def _error_message(self):
        message = self._content.get('message', '')
        if message is not None and message != '':
            return message
        return self._content.get('error', '')


class PlainResponse(Response):
    def __init__(self, response):
        super(PlainResponse, self).__init__(response.status_code, response.text, response.headers)

    def _error_code(self):
        return UNKNOWN_ERROR

    def _error_message(self):
        return self._content


class EmptyResponse(Response):
    def __init__(self, status_code):
        super(EmptyResponse, self).__init__(status_code, '', {})

    def _error_code(self):
        return UNKNOWN_ERROR

    def _error_message(self):
        return ''
