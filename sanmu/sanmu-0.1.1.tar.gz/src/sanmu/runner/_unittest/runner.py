import logging
import unittest
from typing import Type

import ddt
from sanmu.action import RemoteWebDriver, Runner
from sanmu.models import BaseTestSuite
from sanmu.webdriver import get_webdriver

logger = logging.getLogger(__name__)


def create_runner(test_suite: BaseTestSuite):
    return [Runner(case) for case in test_suite.case_list]


def create_tests(test_suite: BaseTestSuite) -> Type[unittest.TestCase]:
    @ddt.ddt
    class Test(unittest.TestCase):
        _test_name = test_suite.info.name
        driver: RemoteWebDriver

        @classmethod
        def setUpClass(cls) -> None:
            cls.driver = get_webdriver(test_suite.info.browser)

        @classmethod
        def tearDownClass(cls) -> None:
            cls.driver.quit()

        @ddt.data(*create_runner(test_suite))
        def test(self, runner: Runner):
            runner.run(self)

        def id(self) -> str:
            return "%s.%s" % (self._test_name, self._testMethodName)

        def __str__(self):
            return "%s (%s:%s)" % (
                self._testMethodName,
                "SanmuTestCae",
                self._test_name,
            )

    return Test
