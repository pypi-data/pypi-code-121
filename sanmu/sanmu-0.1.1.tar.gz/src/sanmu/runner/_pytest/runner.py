import pytest
from sanmu.excel import load_exce_all_sheet
from sanmu.models import BaseTestSuite
from sanmu.runner._unittest.runner import create_tests

from _pytest.python import PyCollector
from _pytest.unittest import UnitTestCase as pytestUnitTestCase


class MyPlugin:
    def pytest_collect_file(self, parent, path):
        if path.ext == ".xlsx" and path.basename.startswith("test"):
            return ExcelFile.from_parent(parent, fspath=path)

    def pytest_html_results_table_row(self, report, cells):
        """fix： pytest-html文件名乱码问题"""
        if report.fspath.endswith(".xlsx"):
            from py.xml import html

            cells[1] = html.td(report.nodeid, class_="col-name")


class ExcelFile(pytest.File, PyCollector):
    def _getobj(self):
        return self

    def collect(self):
        for _suite_data in load_exce_all_sheet(self.fspath):
            suite = BaseTestSuite(**_suite_data)

            obj = create_tests(suite)
            # yield ExcelItem.from_parent(self, suite=suite, case=case)
            item = UnitTestCase.from_parent(
                self,
                name=suite.info.name,
                obj=obj,
            )
            yield item


class UnitTestCase(pytestUnitTestCase):
    @classmethod
    def from_parent(cls, parent, *, name, obj=None):
        """The public constructor."""
        s = super().from_parent(name=name, parent=parent)
        s.obj = obj
        return s
