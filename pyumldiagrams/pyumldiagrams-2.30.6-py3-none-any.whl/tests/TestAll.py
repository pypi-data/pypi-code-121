
from typing import List

from logging import Logger
from logging import getLogger

from sys import path as sysPath

from importlib import import_module

from glob import glob

from unittest import TestResult
from unittest import TextTestRunner
from unittest.suite import TestSuite

from HtmlTestRunner import HTMLTestRunner

from argparse import ArgumentParser
from argparse import Namespace


class TestAll:
    """
    The class that can run our unit tests in various formats
    """
    REPORT_NAME: str = 'PDFDiagramming'
    NOT_TESTS:   List[str] = ['TestAll', 'TestTemplate', 'TestBase', 'TestConstants', 'TestDiagramParent']

    VERBOSITY_QUIET:   int = 0  # Print the total numbers of tests executed and the global result
    VERBOSITY_DEFAULT: int = 1  # VERBOSITY_QUIET plus a dot for every successful test or a F for every failure
    VERBOSITY_VERBOSE: int = 2  # Print help string of every test and the result
    VERBOSITY_LOUD:    int = 3  # ??

    def __init__(self):

        self._setupSystemLogging()

        self.logger: Logger = getLogger(__name__)

        self._testSuite: TestSuite = self._getTestSuite()

    def runTextTestRunner(self) -> int:

        status: TestResult = TextTestRunner(verbosity=TestAll.VERBOSITY_QUIET).run(self._testSuite)
        self.logger.info(f'Test Suite Status: {status}')
        if len(status.failures) != 0:
            return 1
        else:
            return 0

    def runHtmlTestRunner(self) -> int:

        runner = HTMLTestRunner(report_name=f'{TestAll.REPORT_NAME}', combine_reports=True, add_timestamp=True)
        status = runner.run(self._testSuite)
        if len(status.failures) != 0:
            return 1
        else:
            return 0

    def _setupSystemLogging(self):
        """
        Read the unit test logging configuration file
        """
        from tests.TestBase import TestBase

        TestBase.setUpLogging()

    def _getTestSuite(self) -> TestSuite:
        """

        Returns:
            A suite of all tests in the unit test directory
        """
        modules: List[str] = self.__getTestableModuleNames()
        fSuite: TestSuite = TestSuite()
        for module in modules:
            try:
                fixedName: str = module.replace('/', '.')
                m = import_module(fixedName)
                # I do not know how to declare a module that has a specific method/function
                # noinspection PyUnresolvedReferences
                fSuite.addTest(m.suite())
            except (ValueError, Exception) as e:
                self.logger.error(f'Module import problem with: {module}:  {e}')
        return fSuite

    def __getTestableModuleNames(self) -> List[str]:
        """
        Removes modules that are not unit tests

        Assumes the "tests" package is visible from the current directory

        Returns:
            A list of module names that we can find in this package
        """
        fModules = glob("tests/Test*.py")
        # remove .py extension
        baseModules = list(map(lambda x: x[:-3], fModules))
        baseModules = self.__removeNotTests(baseModules)

        fModules = glob("tests/pdf/Test*.py")
        pdfModules = list(map(lambda x: x[:-3], fModules))
        pdfModules = self.__removeNotTests(pdfModules)

        testModules = baseModules + pdfModules

        fModules = glob("tests/image/Test*.py")
        imgModules = list(map(lambda x: x[:-3], fModules))
        imgModules = self.__removeNotTests(imgModules)

        testModules = testModules + imgModules

        return testModules

    def __removeNotTests(self, testModules):

        for doNotTest in TestAll.NOT_TESTS:
            try:
                testModules.remove(f'tests/{doNotTest}')
            except ValueError:
                pass     # don't care
        return testModules


def main():

    if ".." not in sysPath:
        sysPath.append("..")  # access to the classes to test

    cliParser: ArgumentParser = ArgumentParser(description='Run all unit tests')

    # Add the arguments
    cliParser.add_argument('-p',
                           '--produce-html-results',
                           action='store_true',
                           help='Produce HTML Test')
    cliParser.add_argument('-c',
                           '--cleanup',
                           action='store_true',
                           help='Clean up generated tests')

    testAll: TestAll = TestAll()

    args: Namespace = cliParser.parse_args()

    if args.produce_html_results:
        status: int = testAll.runHtmlTestRunner()
    else:
        status: int = testAll.runTextTestRunner()

    return status


if __name__ == "__main__":
    cliStatus: int = main()
    exit(cliStatus)
