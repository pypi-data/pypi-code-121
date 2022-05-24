import errno
import os
import signal

import pytest
import logging
import traceback

from urllib.parse import urlsplit
from functools import wraps
from selenium.common.exceptions import WebDriverException

from promium.assertions import (
    WebDriverSoftAssertion,
    RequestSoftAssertion
)
from promium.exceptions import PromiumException
from promium.browsers import (
    FirefoxBrowser, ChromeBrowser, OperaBrowser, RemoteBrowser
)
from promium.logger import (
    request_logging,
    logger_for_loading_page
)


TEST_PROJECT = os.environ.get('TEST_PROJECT')
TEST_CASE = os.environ.get('TEST_CASE')

log = logging.getLogger(__name__)

DRIVERS = {
    'firefox': 'Firefox',
    'chrome': 'Chrome',
    'safari': 'Safari',
    'opera': 'Opera',
    'ie': 'Ie',
}

MAX_LOAD_TIME = 10


def timeout(seconds=5, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorator


@timeout(60)
def create_driver(
        device, proxy_server=None, env_var='SE_DRIVER', default='chrome://'
):
    """
    Examples:

        - 'chrome://'
        - 'firefox://'
        - 'opera://'

    """
    driver_options = {
        "device": device,
        "proxy_server": proxy_server,
        "is_headless": (
            True if os.environ.get("HEADLESS") == "Enabled" else False
        ),
    }

    driver_dsn = os.environ.get(env_var) or default

    if not driver_dsn:
        raise RuntimeError(f'Selenium WebDriver is not set in the {env_var} '
                           f'environment variable')
    try:
        scheme, netloc, url, _, _ = urlsplit(driver_dsn)
    except ValueError:
        raise ValueError(f'Invalid url: {driver_dsn}')

    if scheme in DRIVERS:
        if scheme == "chrome":
            return ChromeBrowser(**driver_options)
        elif scheme == "firefox":
            return FirefoxBrowser(device=device)
        elif scheme == "opera":
            return OperaBrowser(device=device)
        else:
            raise ValueError(f'Unknown client specified: {scheme}')

    elif scheme.startswith('http+'):
        proto, _, client = scheme.partition('+')
        if not netloc:
            raise ValueError(f'Network address is not specified: {driver_dsn}')

        if client not in DRIVERS:
            raise ValueError(f'Unknown client specified: {client}')

        driver_options["client"] = client
        driver_options["hub"] = f'{proto}://{netloc}{url}'

        try:
            driver = RemoteBrowser(**driver_options)
        except WebDriverException:
            log.warning("Second attempt for remote driver connection.")
            driver = RemoteBrowser(**driver_options)
        except KeyError as e:
            log.warning(str(e))
            if "status" in str(e):
                raise PromiumException(
                    "Session timed out because the browser was idle too long."
                    "Or no free slots for create new session."
                )
            raise
        return driver

    raise ValueError(f'Unknown driver specified: {driver_dsn}')


class TDPException(Exception):

    def __init__(self, *args):
        self.message = (
            "exception caught during execution test data preparing.\n"
            "Look at the original traceback:\n\n%s\n"
            ) % ("".join(traceback.format_exception(*args)))

    def __str__(self):
        return self.message


class TDPHandler:
    """
    TDP - Test Data Preparation
    context manager for handling any exception
    during execution test data preparing.
    We need to raise a specific custom exceptions.
    :example:
    with self.tdp_handler():
        some code
    """

    def __init__(self):
        pass

    def __enter__(self):
        log.info("[TDP] Start test data preparing...")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        log.info("[TDP] Finish test data preparing")
        if exc_type:
            raise TDPException(exc_type, exc_value, exc_tb)
        return


class TestCase(object):
    xrequestid = None
    test_case_url = None
    assertion_errors = None
    proxy_server = None

    def tdp_handler(self):
        """
        Use this context manager for prepare of test data only,
        not for business logic!
        """
        return TDPHandler()

    def setup_method(self, method):
        check_test_case = os.environ.get("TEST_CASE")
        if check_test_case == "True" and not self.test_case_url:
            raise PromiumException("Test don't have a test case url.")


@pytest.mark.usefixtures("driver_init")
class WebDriverTestCase(TestCase, WebDriverSoftAssertion):
    driver = None

    @logger_for_loading_page
    def get_url(self, url, cleanup=True):
        self.driver.get(url)
        if cleanup:
            try:
                self.driver.execute_script(
                    'localStorage.clear()'
                )
            except WebDriverException:
                pass
        return url


@pytest.mark.usefixtures("request_init")
class RequestTestCase(TestCase, RequestSoftAssertion):
    session = None
    proxies = {}

    def get_response(
        self, url, method="GET", timeout=10, cookies=None, **kwargs
    ):
        self.session.url = url
        self.session.status_code = None
        request_cookies = {'xrequestid': self.xrequestid}
        if cookies:
            request_cookies.update(cookies)
        response = self.session.request(
            method=method,
            url=url,
            timeout=timeout,
            verify=False,
            cookies=request_cookies,
            hooks=dict(response=request_logging),
            **kwargs,
        )
        self.session.status_code = response.status_code
        return response
