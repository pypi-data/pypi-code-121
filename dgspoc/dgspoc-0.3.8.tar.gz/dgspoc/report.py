"""Module containing the logic for report of test execution"""

import re
from os import path
from glob import glob

import platform
import robot
import pytest

from datetime import datetime

from collections import OrderedDict

from dgspoc.constant import ECODE
from dgspoc.constant import FWTYPE
from dgspoc.exceptions import ReportError

from dgspoc.utils import DotObject
from dgspoc.utils import Printer

from xml.etree import ElementTree


class DGSReport:
    def __init__(self, *report_files, detail=False):
        if not report_files:
            raise ReportError('CANT generate report without report file.')

        self.report_files = report_files
        self.detail = detail
        self.exit_code = ECODE.PASSED

    def get_report_title(self, framework):      # noqa
        node = DotObject(py_ver=platform.python_version(),
                         rf_ver=robot.__version__,
                         pytest_ver=pytest.__version__,
                         os_name=platform.system())
        if framework == FWTYPE.UNITTEST:
            fmt = 'Unittest Report - Unittest {py_ver} - Python {py_ver} on {os_name}'
        elif framework == FWTYPE.PYTEST:
            fmt = 'Pytest Report - Pytest {pytest_ver} - Python {py_ver} on {os_name}'
        else:
            fmt = 'Robotframework Report - Robot {rf_ver} - Python {py_ver} on {os_name}'

        report_title = fmt.format(**node)
        return report_title

    def generate(self):
        lst = []
        for report_file in self.report_files:
            file_obj = DGSReportFile(report_file)
            if file_obj.is_unittest:
                report_content = self.generate_unittest_report(report_file)
            elif file_obj.is_pytest:
                report_content = self.generate_pytest_report(report_file)
            else:
                report_content = self.generate_robotframework_report(report_file)

            if report_content.strip():
                lst and lst.append('')
                lst.append(report_content)

        all_reports = '\n'.join(lst)
        return all_reports

    def generate_unittest_report(self, file_name):
        tree = ElementTree.parse(file_name)
        root = tree.getroot()
        testsuites = root.findall('testsuite')

        od = OrderedDict()

        total_failed = 0

        for testsuite in testsuites:
            for testcase in testsuite:
                name = testcase.attrib.get('file')
                result = od.get(name, DotObject(total=0, passed=0, failed=0, skipped=0))
                result.name = name
                od[name] = result
                result.total += 1
                if testcase.findall('failure') or testcase.findall('error'):
                    result.failed += 1
                result.passed = result.total - result.failed
            failures = int(testsuite.attrib.get('failures'))
            errors = int(testsuite.attrib.get('errors'))

            if failures or errors:
                total_failed += 1

        if total_failed:
            self.exit_code = ECODE.FAILED

        fmt = ('  - Test case: {name} (Total: {total} / Passed: {passed} / '
               'Failed: {failed} / Skipped: {skipped})')
        lst = []
        for testcase_name, val in od.items():
            lst.append(fmt.format(**val))

        total = len(od)
        total_passed = total - total_failed
        fmt = 'Total Test Cases: %s / Passed: %s / Failed: %s'
        report_summary = fmt % (total, total_passed, total_failed)
        report_title = self.get_report_title(FWTYPE.UNITTEST)
        header = [report_title, '-' * len(report_title), report_summary]
        header_txt = Printer.get(header)

        testcases_txt = '\n'.join(lst)

        if self.detail:
            report = '%s\n%s' % (header_txt, testcases_txt)
        else:
            report = header_txt

        return report

    def generate_pytest_report(self, file_name):
        tree = ElementTree.parse(file_name)
        root = tree.getroot()
        testsuite = root.find('testsuite')

        od = OrderedDict()

        result = None
        total_failed = 0

        for testcase in testsuite:
            name = testcase.attrib.get('classname').rsplit('.', 1)[0]
            result = od.get(name, DotObject(total=0, passed=0, failed=0, skipped=0))
            result.name = name
            od[name] = result
            result.total += 1
            if testcase.findall('failure') or testcase.findall('error'):
                result.failed += 1
            result.passed = result.total - result.failed
        else:
            if result and result.failed:
                total_failed += 1

        if total_failed:
            self.exit_code = ECODE.FAILED

        fmt = ('  - Test case: {name} (Total: {total} / Passed: {passed} / '
               'Failed: {failed} / Skipped: {skipped})')
        lst = []
        for testcase_name, val in od.items():
            lst.append(fmt.format(**val))

        total = len(od)
        total_passed = total - total_failed
        fmt = 'Total Test Cases: %s / Passed: %s / Failed: %s'
        report_summary = fmt % (total, total_passed, total_failed)
        report_title = self.get_report_title(FWTYPE.PYTEST)
        header = [report_title, '-' * len(report_title), report_summary]
        header_txt = Printer.get(header)

        testcases_txt = '\n'.join(lst)

        if self.detail:
            report = '%s\n%s' % (header_txt, testcases_txt)
        else:
            report = header_txt

        return report

    def generate_robotframework_report(self, file_name):
        tree = ElementTree.parse(file_name)
        root = tree.getroot()

        # suite_node = root.find('suite')
        statistics_suite = root.find('statistics/suite')
        errors_node = root.find('errors')

        lst = []

        fmt = ('  - Test case: {name} (Total: {total} / Passed: {passed} / '
               'Failed: {failed} / Skipped: {skipped})')
        total_failed = 0
        result = None
        for index, node in enumerate(statistics_suite):
            if index == 0:
                continue

            result = DotObject(
                name=node.text,
                passed=int(node.attrib.get('pass')),
                failed=int(node.attrib.get('fail')),
                skipped=int(node.attrib.get('skip'))
            )
            result.total = result.passed + result.failed + result.skipped
            lst.append(fmt.format(**result))
        else:
            if result and result.failed:
                total_failed += 1

        if total_failed:
            self.exit_code = ECODE.FAILED

        total = len(statistics_suite) - 1
        total_passed = total - total_failed
        fmt = 'Total Test Cases: %s / Passed: %s / Failed: %s'
        report_summary = fmt % (total, total_passed, total_failed)
        report_title = self.get_report_title(FWTYPE.ROBOTFRAMEWORK)
        header = [report_title, '-' * len(report_title), report_summary]
        header_txt = Printer.get(header)

        testcases_txt = '\n'.join(lst)

        errors = []
        for index, node in enumerate(errors_node):
            error_no = index + 1
            errors.append(Printer.get('Error #%s' % error_no))
            errors.append(node.text)

        errors_txt = '\n'.join(errors)

        if self.detail:
            report = '%s\n%s' % (header_txt, testcases_txt)
            if errors_txt:
                report = '%s\n%s' % (report, errors_txt)
        else:
            report = header_txt

        return report

    @classmethod
    def generate_report(cls, directory=''):
        report_files = DGSReportFile.get_report_files(directory=directory)
        report = cls(*report_files)

        report_content = report.generate()
        return report_content

    
class DGSReportFile:
    def __init__(self, filename):
        self.filename = str(filename).strip()
        self.basename = path.basename(self.filename)

    @property
    def mark_time(self):
        if self.is_report_file:
            if self.is_unittest:
                fmt = 'unittest_report_%Y%b%d_%H%M%S.xml'
            elif self.is_pytest:
                fmt = 'pytest_report_%Y%b%d_%H%M%S.xml'
            else:
                fmt = 'robotframework_output_%Y%b%d_%H%M%S.xml'
            dt = datetime.strptime(self.basename, fmt)
            return dt
        else:
            dt = datetime(1900, 1, 1)
            return dt

    @property
    def is_report_file(self):
        chk = self.is_unittest
        chk |= self.is_pytest
        chk |= self.is_robotframework
        return chk
    
    @property
    def is_unittest(self):
        chk = self.check_report_file(FWTYPE.UNITTEST)
        return chk
    
    @property
    def is_pytest(self):
        chk = self.check_report_file(FWTYPE.PYTEST)
        return chk
    
    @property
    def is_robotframework(self):
        chk = self.check_report_file(FWTYPE.ROBOTFRAMEWORK)
        return chk

    def check_report_file(self, framework):
        other = 'output' if framework == FWTYPE.ROBOTFRAMEWORK else 'report'
        prefix = '%s_%s' % (framework, other)
        fmt = '%s_[0-9]{4}[a-z]{3}[0-9]{2}_[0-9]{6}[.]xml'
        pattern = fmt % prefix
        match = re.match(pattern, self.basename, re.I)
        return bool(match)

    @classmethod
    def get_report_files(cls, directory=''):
        directory = str(directory).strip()

        lookups = ['unittest_report_*_*.xml',
                   'pytest_report_*_*.xml',
                   'robotframework_output_*_*.xml']
        file_names = []
        for lookup in lookups:
            file_path = path.join(directory, lookup)
            file_names += glob(file_path)
        report_files = cls.get_latest_report_files(file_names)

        return report_files

    @classmethod
    def get_latest_report_file(cls, file1, file2):
        file_obj1 = cls(file1)
        file_obj2 = cls(file2)

        if file_obj1.is_report_file and file_obj2.is_report_file:
            if file_obj1.mark_time >= file_obj2.mark_time:
                return file1
            else:
                return file2
        elif file_obj1.is_report_file:
            return file1
        elif file_obj2.is_report_file:
            return file2
        else:
            return ''

    @classmethod
    def get_latest_report_files(cls, file_names):
        if not file_names:
            return file_names

        base_file = file_names[0]
        lst = []
        for file_name in file_names:
            latest_file = cls.get_latest_report_file(base_file, file_name)
            if latest_file and latest_file not in lst:
                lst.append(latest_file)

        if len(lst) > 1:
            latest_dt = cls(lst[0]).mark_time
            for file_name in lst:
                mark_time = cls(file_name).mark_time
                if mark_time >= latest_dt:
                    latest_dt = mark_time

            latest_report_files = []
            for file_name in lst:
                if cls(file_name).mark_time == latest_dt:
                    latest_report_files.append(file_name)
            return latest_report_files
        else:
            return lst
