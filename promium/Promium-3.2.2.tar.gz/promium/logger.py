import allure
import logging
import os
import py
import pytest
import re
from functools import wraps

from selenium.common.exceptions import WebDriverException


log = logging.getLogger(__name__)

MAX_SYMBOLS = 510
TABS_FORMAT = " " * 20


def repr_console_errors(console_errors, tabs=TABS_FORMAT):
    return "\n{tabs_format}".format(tabs_format=tabs).join(
        ">>> [CONSOLE ERROR] %s" % error for error in set(console_errors)
    )


def repr_args(*args, **kwargs):
    return "{args}{mark}{kwargs}".format(
        args=", ".join(list(map(lambda x: str(x), args))) if args else "",
        kwargs=", ".join(
            "%s=%s" % (k, v) for k, v in kwargs.items()
        ) if kwargs else "",
        mark=", " if args and kwargs else ""
    )


def find_console_browser_errors(driver):
    try:
        return set(map(
            lambda x: x["message"],
            list(filter(
                lambda x: x["level"] == "SEVERE", driver.get_log("browser")
            ))
        ))
    except WebDriverException as e:
        log.warning(f"Exception when reading Browser Console log: {str(e)}")
        return None


def find_component_render_errors(console_errors):
    return list(filter(lambda x: 'render error' in x, console_errors))


def logger_for_element_methods(fn):

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        res = fn(self, *args, **kwargs)
        console_errors = find_console_browser_errors(self.driver)
        is_check = os.environ.get('CHECK_CONSOLE')
        if console_errors:
            log.warning(
                "Browser console js error found:\n"
                "{tabs_format}{console_errors}\n"
                "{tabs_format}Url: {url}\n"
                "{tabs_format}Action: {class_name}"
                "({by}={locator})"
                ".{method}({args})".format(
                    tabs_format=TABS_FORMAT,
                    class_name=self.__class__.__name__,
                    by=self.by,
                    locator=self.locator,
                    method=fn.__name__,
                    args=repr_args(*args, **kwargs),
                    url=self.driver.current_url,
                    console_errors=repr_console_errors(
                        console_errors
                    )
                )
            )

            error_tmpl = (
                "Url: {url}\n"
                "Action: {class_name}({by}={locator})"
                ".{method}({args})\n"
                "{end_symbol}".format(
                    class_name=self.__class__.__name__,
                    by=self.by,
                    locator=self.locator,
                    method=fn.__name__,
                    args=repr_args(*args, **kwargs),
                    url=self.driver.current_url,
                    end_symbol="-" * 75
                )
            )
            is_check_render = os.environ.get('CHECK_RENDER_ERRORS')
            if is_check_render and hasattr(self.driver, "render_errors"):
                render_errors = find_component_render_errors(console_errors)
                for err in set(render_errors):
                    self.driver.render_errors.append(
                        f">>> [RENDER ERROR] {err}\n {error_tmpl}"
                    )
            if is_check and hasattr(self.driver, "console_errors"):
                for err in set(console_errors):
                    self.driver.console_errors.append(
                        f">>> [CONSOLE ERROR] {err}\n {error_tmpl}"
                    )
        return res
    return wrapper


def add_logger_to_base_element_classes(cls):
    for name, method in cls.__dict__.items():
        log.info("%s, %s" % (name, method))
        if (not name.startswith('_') and
                hasattr(method, '__call__') and name != "lookup"):
            setattr(cls, name, logger_for_element_methods(method))
    return cls


def logger_for_loading_page(fn):

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        res = fn(self, *args, **kwargs)
        if os.environ.get('CHECK_CONSOLE'):
            console_errors = find_console_browser_errors(self.driver)
            if console_errors:
                log.warning(
                    "Browser console js error found:\n"
                    "{tabs_format}{console_errors}\n"
                    "{tabs_format}Url: {url}\n"
                    "{tabs_format}Action: wait for page loaded ...".format(
                        tabs_format=TABS_FORMAT,
                        url=self.driver.current_url,
                        console_errors=repr_console_errors(console_errors)
                    )
                )
                if hasattr(self.driver, "console_errors"):
                    for err in set(console_errors):
                        self.driver.console_errors.append(
                            ">>> [CONSOLE ERROR] {err}\n"
                            "Url: {url}\n"
                            "Action: wait for page loaded ...\n"
                            "{end_symbol}".format(
                                url=self.driver.current_url,
                                err=err,
                                end_symbol="-" * 75
                            )
                        )
        return res
    return wrapper


IGNORE_LOG_MESSAGES = [
    "InsecureRequestWarning: Unverified HTTPS request is being made. "
    "Adding certificate verification is strongly advised.",
    "Starting new HTTP connection",
    "Starting new HTTPS connection"
]


class LoggerFilter(logging.Filter):

    def filter(self, record):
        if hasattr(record, "msg"):
            is_ignore = any(set(filter(
                lambda x: x in record.msg, IGNORE_LOG_MESSAGES
            )))
            if is_ignore:
                return False
        return record.levelno > 10


class Logger(object):

    def pytest_runtest_setup(self, item):
        item.capturelog_handler = LoggerHandler()
        item.capturelog_handler.setFormatter(logging.Formatter(
            "%(asctime)-12s%(levelname)-8s%(message)s\n", "%H:%M:%S"
        ))
        root_logger = logging.getLogger()
        item.capturelog_handler.addFilter(LoggerFilter())
        root_logger.addHandler(item.capturelog_handler)
        root_logger.setLevel(logging.NOTSET)

    @pytest.mark.hookwrapper
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if hasattr(item, "capturelog_handler"):
            if call.when == 'teardown':
                root_logger = logging.getLogger()
                root_logger.removeHandler(item.capturelog_handler)
            if not report.passed:
                longrepr = getattr(report, 'longrepr', None)
                if hasattr(longrepr, 'addsection'):
                    captured_log = item.capturelog_handler.stream.getvalue()
                    if captured_log:
                        longrepr.sections.insert(
                            len(longrepr.sections),
                            ('Captured log', "\n%s" % captured_log, "-")
                        )
                        if item.config.getoption("--allure-report"):
                            allure.attach(
                                captured_log, name='CAPTURED LOG',
                                attachment_type='text/plain'
                            )
            if call.when == 'teardown':
                item.capturelog_handler.close()
                del item.capturelog_handler


class LoggerHandler(logging.StreamHandler):

    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.stream = py.io.TextIO()
        self.records = []

    def close(self):
        logging.StreamHandler.close(self)
        self.stream.close()


def request_logging(request, *args, **kwargs):
    content = str(request.content)
    warning_message = (
        "[Python request] STATUS CODE: {status_code}, LINK: {link}\n"
        "{tabs}METHOD: {method}\n"
        "{tabs}BODY: {body}\n"
        "{tabs}RESPONSE CONTENT: "
        "{content}{ellipsis} ({length} symbols)\n".format(
            status_code=request.status_code,
            method=request.request.method,
            link=request.url,
            body=request.request.body,
            content=re.sub(r'\s+', ' ', content)[:MAX_SYMBOLS],
            ellipsis=" ..." if len(content) > MAX_SYMBOLS else "",
            length=len(request.content),
            tabs=" " * 12
        )
    )
    if 400 <= request.status_code < 500:
        log.warning(warning_message)
    elif request.status_code >= 500:
        log.error(warning_message)
    else:
        log.info(
            "[Python request] STATUS CODE: {status_code}, LINK: {link}".format(
                status_code=request.status_code, link=request.url
            )
        )
