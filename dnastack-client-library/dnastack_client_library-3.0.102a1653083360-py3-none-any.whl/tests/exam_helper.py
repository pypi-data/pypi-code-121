import datetime
from pprint import pformat

import time
from dataclasses import dataclass
from threading import Lock

from typing import Callable, List, Optional, Any, Dict, Type, Iterable
from unittest import TestCase

from contextlib import contextmanager

from urllib.parse import urljoin
from uuid import uuid4

from dnastack.client.service_registry.models import ServiceType
from dnastack.configuration.models import ServiceEndpoint, OAuth2Authentication
from dnastack.common.environments import env
from dnastack.common.logger import get_logger, alert_for_deprecation

_logger = get_logger('exam_helper')

client_id = env('E2E_CLIENT_ID', required=True)
client_secret = env('E2E_CLIENT_SECRET', required=True)

wallet_url = env('E2E_WALLET_BASE_URL', required=True)
passport_url = env('E2E_PASSPORT_BASE_URL', default=wallet_url)
redirect_url = env('E2E_REDIRECT_URL', default=wallet_url)

authorization_endpoint = urljoin(wallet_url, '/oauth/authorize')
device_code_endpoint = urljoin(wallet_url, '/oauth/device/code')
personal_access_endpoint = urljoin(passport_url, '/login/token')
token_endpoint = urljoin(wallet_url, '/oauth/token')


def initialize_test_endpoint(resource_url: str,
                             service_type: Optional[str] = None,
                             secure: bool = True,
                             type: Optional[ServiceType] = None) -> ServiceEndpoint:
    if service_type:
        alert_for_deprecation('initialize_test_endpoint: "adapter_type" is now deprecated')

    auth_info = OAuth2Authentication(
        type='oauth2',
        client_id=client_id,
        client_secret=client_secret,
        grant_type='client_credentials',
        resource_url=resource_url,
        token_endpoint=token_endpoint,
    ).dict() if secure else None

    return ServiceEndpoint(
        id=f'auto-test-{uuid4()}',
        url=resource_url,
        authentication=auth_info,
        type=type,
    )


@contextmanager
def measure_runtime(description: str, log_level: str = None):
    _logger = get_logger('timer')
    log_level = log_level or 'debug'
    start_time = time.time()
    yield
    getattr(_logger, log_level)(f'{description} ({time.time() - start_time:.3f}s)')


def assert_equal(expected: Any, given: Any):
    """Assert equality (to be used outside unittest.TestCase)"""
    assert expected == given, f'Expected {pformat(expected)}, given {pformat(given)}'


class CallableProxy():
    def __init__(self, operation: Callable, args, kwargs):
        self.operation = operation
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        self.operation(*self.args, **self.kwargs)


class ReversibleTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(ReversibleTestCase, self).__init__(*args, **kwargs)
        self._revert_operation_lock = Lock()
        self._revert_operations: List[CallableProxy] = list()

    def after_this_test(self, operation: Callable, *args, **kwargs):
        with self._revert_operation_lock:
            self._revert_operations.insert(0, CallableProxy(operation, args, kwargs))

    def tearDown(self) -> None:
        with self._revert_operation_lock:
            while self._revert_operations:
                revert_operation = self._revert_operations.pop(0)
                revert_operation()
            self._revert_operations.clear()


class BaseTestCase(TestCase):
    def assert_not_empty(self, obj, message: Optional[str] = None):
        self.assertIsNotNone(obj, message)
        self.assertGreater(len(obj), 0, message)

    def skip_until(self, iso_date_string: str, reason: Optional[str] = None):
        expiry_time = datetime.date.fromisoformat(iso_date_string)
        current_time = datetime.date.fromtimestamp(time.time())

        if (current_time - expiry_time).days > 0:
            self.fail("This test requires your attention.")
        else:
            self.skipTest(f"This test will be skipped until {iso_date_string}. (Reason: {reason})")

    def drain_iterable(self, iterable: Iterable[Any]):
        return [i for i in iterable]

    # noinspection PyMethodMayBeStatic
    def retry_if_fail(self, test_operation: Callable, max_run_count: int = 3, intermediate_cleanup: Callable = None):
        current_run_count = max_run_count
        while True:
            current_run_count -= 1
            try:
                test_operation()
                break
            except Exception:
                if current_run_count > 0:
                    if intermediate_cleanup:
                        intermediate_cleanup()
                    time.sleep(10)
                    continue
                else:
                    raise RuntimeError(f'Still failed after {max_run_count} run(s)')


@dataclass(frozen=True)
class DataConversionSample:
    id: str
    format: str
    content: str
    expected_type: Type
    expectations: List[Callable[[Any], None]]

    @classmethod
    def make(cls, format: str, content: Any, expected_type: Type,
             expectations: List[Callable[[Any], None]] = None):
        return cls(
            f'{format}__{time.time()}'.replace(r' ', r'_').replace(r'.', r'_'),
            format,
            content,
            expected_type,
            expectations or [],
        )

    @classmethod
    def date(cls, content: str, expectations: List[Callable[[Any], None]] = None):
        return cls.make('date', content, datetime.date, expectations)

    @classmethod
    def time(cls, content: str, expectations: List[Callable[[Any], None]] = None):
        return cls.make('time', content, datetime.time, expectations)

    @classmethod
    def time_with_time_zone(cls, content: str, expectations: List[Callable[[Any], None]] = None):
        return cls.make('time with time zone', content, datetime.time, expectations)

    @classmethod
    def timestamp(cls, content: str, expectations: List[Callable[[Any], None]] = None):
        return cls.make('timestamp', content, datetime.datetime, expectations)

    @classmethod
    def timestamp_with_time_zone(cls, content: str, expectations: List[Callable[[Any], None]] = None):
        return cls.make('timestamp with time zone', content, datetime.datetime, expectations)

    @classmethod
    def interval_year_to_month(cls, content: str, expectations: List[Callable[[Any], None]] = None):
        return cls.make('interval year to month', content, str, expectations)

    @classmethod
    def interval_day_to_second(cls, content: str, expectations: List[Callable[[Any], None]] = None):
        return cls.make('interval day to second', content, datetime.timedelta, expectations)

    def get_schema(self) -> Dict[str, str]:
        return dict(type='string', format=self.format)
