from io import BytesIO
import json
from mock import patch
from unittest.case import TestCase
from urllib.parse import urljoin
from uuid import uuid4

import requests
import requests_mock

from rebotics_sdk.providers.base import (
    UniqueRequestProxy, ReboticsBaseProvider, remote_service, RetryableException
)
from tests.utils import get_random_string


def mirror_request_data_to_json(request: requests.Request, _context) -> dict:
    """
    Mirrors the incoming request method and headers to the response for test purposes.
    Some standard headers are ignored to not litter up tests
    """
    ignored_headers = ('User-Agent', 'Accept-Encoding', 'Accept', 'Connection',
                       'Content-Length', 'Content-Type')
    return {
        'method': request.method,
        'headers': {
            header: value
            for header, value in request.headers.items()
            if header not in ignored_headers
        }
    }


# To avoid hitting real APIs
@requests_mock.Mocker()
class UniqueRequestProxyIntegrationTest(TestCase):
    """
    Integration tests for UniqueRequestProxy
    """
    class TestProvider(ReboticsBaseProvider):
        TEST_HEADER_NAME = 'x-reb-test-req-uuid'

        proxy_class = UniqueRequestProxy
        proxy_config = {
            'request_uid_header_name': TEST_HEADER_NAME
        }

        TEST_METHOD_URI = '/dummy/'

        @remote_service(TEST_METHOD_URI)
        def dummy_call(self, method: str):
            fn = getattr(self.session, method.lower())
            return fn()

        @remote_service(TEST_METHOD_URI,
                        request_uid_value=lambda **kwargs: kwargs['json']['some_uuid'])
        def dummy_call_external_uuid(self, method: str, some_uuid: str):
            fn = getattr(self.session, method.lower())
            return fn(json={'some_uuid': some_uuid})

    def setUp(self):
        self.host_url = 'https://' + get_random_string(6) + '/'
        self.provider = self.TestProvider(self.host_url)
        self.api_url = urljoin(self.host_url, self.provider.TEST_METHOD_URI)

    # To have better control over generated UUID
    @patch('rebotics_sdk.providers.base.uuid4')
    def test_post_and_put_contain_unique_request_header(
            self, mock_requests, mock_uuid4):
        """
        Checks that methods that are based on PUT and POST requests will produce a
        request containing deduplication header
        """
        test_uuid4 = str(uuid4())
        mock_uuid4.return_value = test_uuid4

        methods = ('PUT', 'POST')
        for method in methods:
            with self.subTest(msg=f'{method}'):
                mock_requests.register_uri(
                    method,
                    self.api_url,
                    json=mirror_request_data_to_json
                )

                result = self.provider.dummy_call(method)

                self.assertEqual(result, {
                    'method': method,
                    'headers': {
                        self.provider.TEST_HEADER_NAME: test_uuid4
                    }
                })

    def test_other_methods_work_normally(self, mock_requests):
        """
        Checks that methods that are based on OPTIONS, HEAD, GET, PATCH and DELETE
        requests will produce a request without deduplication header as usual
        """
        methods = ('OPTIONS', 'HEAD', 'GET', 'PATCH', 'DELETE')
        for method in methods:
            with self.subTest(msg=f'{method}'):
                mock_requests.register_uri(
                    method,
                    self.api_url,
                    json=mirror_request_data_to_json
                )

                result = self.provider.dummy_call(method)

                self.assertEqual(result, {'method': method, 'headers': {}})

    def test_external_uuid_is_taken_to_header(self, mock_requests):
        """
        Checks that if method is configured to use external UUID, and it's specified,
        then this external value will be picked to the header
        """
        test_uuid4 = str(uuid4())
        method = 'POST'
        mock_requests.register_uri(
            method,
            self.api_url,
            json=mirror_request_data_to_json
        )

        result = self.provider.dummy_call_external_uuid(
            method,
            some_uuid=test_uuid4
        )

        self.assertEqual(result, {
            'method': method,
            'headers': {
                self.provider.TEST_HEADER_NAME: test_uuid4
            }
        })


class UniqueRequestProxyBaseTestCase(TestCase):
    """
    Base case for unit-testing of UniqueRequestProxy
    """
    def setUp(self):
        self.url = 'https://' + get_random_string(6) + '/'
        self.header_name = 'x-test-request-id'
        self.proxy = UniqueRequestProxy(
            url=self.url,
            headers={},
            timeout=5,
            request_uid_header_name=self.header_name
        )


class TestUniqueRequestProxyRaiseIfErrorStatusCode(UniqueRequestProxyBaseTestCase):
    """
    Unit-tests for `UniqueRequestProxy.raise_if_error_status_code`
    """
    DEFAULT_ERROR_TEXT = 'Another request is already processing'

    def test_424_with_provided_error_text(self):
        """
        Checks that error with code 424, that is usually thrown from Rebotics service,
        is considered as retryable
        """
        test_error_description = 'Request is processing: %s' % get_random_string(6)
        resp = requests.Response()
        resp.raw = BytesIO(bytes(
            json.dumps({'error': test_error_description}),
            encoding='utf8'
        ))
        resp.status_code = 424

        with self.assertRaises(RetryableException) as context:
            self.proxy.raise_if_error_status_code(resp)

        self.assertEqual(context.exception.args[0], test_error_description)

    def test_424_with_no_error_text(self):
        """
        Checks that error with code 424 but without 'error' field is considered
        as retryable
        """
        resp = requests.Response()
        resp.raw = BytesIO(bytes(
            json.dumps({}),
            encoding='utf8'
        ))
        resp.status_code = 424

        with self.assertRaises(RetryableException) as context:
            self.proxy.raise_if_error_status_code(resp)

        self.assertEqual(context.exception.args[0], self.DEFAULT_ERROR_TEXT)

    def test_424_no_json_resp(self):
        """
        Checks that error with code 424 but without json body is considered
        as retryable
        """
        resp = requests.Response()
        resp.raw = BytesIO(bytes(
            'Hi there',
            encoding='utf8'
        ))
        resp.status_code = 424

        with self.assertRaises(RetryableException) as context:
            self.proxy.raise_if_error_status_code(resp)

        self.assertEqual(context.exception.args[0], self.DEFAULT_ERROR_TEXT)
