# -*- coding: utf-8 -*-

import re
import shutil

from inspect import signature
from io import StringIO, TextIOBase
from typing import AnyStr, Tuple, Optional, Callable, Union

from junitparser import JUnitXml
from lxml import etree


class ReportFilter:
    """Report filter"""

    class Summary:
        """Filter summary"""

        @property
        def summary(self) -> Tuple[int, int]:
            """Report summary

            Returns: passed, executed
            """
            raise NotImplementedError

    class Result:
        """Filter result capsule."""

        def __init__(self, report, result, other):
            self._report = report
            self._result = result
            self._other = other
            self._stream = None

        def __del__(self):
            if self._stream and isinstance(self._stream, TextIOBase):
                self._stream.close()

        @staticmethod
        def cached(attr_name):
            """Decorator adding return value cache.

            Args:
                attr_name (str): The attribute to store the value.
            """
            def _cached(fn):
                def __cached(self):
                    value = getattr(self, attr_name)
                    if not value:
                        try:
                            value = fn(self)
                        except RuntimeError as e:
                            value = e
                        setattr(self, attr_name, value)
                    if isinstance(value, RuntimeError):
                        raise value
                    return value
                return __cached
            return _cached

        def getvalue(self) -> str:
            """Get the stream content as string."""
            stream = self.stream
            if hasattr(stream, 'getvalue'):
                return stream.getvalue()
            stream.seek(0)
            return stream.read()

        def write(self, filename: AnyStr):
            """Write filter input to file."""
            with open(filename, "w", encoding='utf-8') as file:
                self.stream.seek(0)
                shutil.copyfileobj(self.stream, file)

        @property
        def stream(self) -> TextIOBase:
            """Retrieve this filters text stream."""
            if self._other:
                return self._other.stream
            return StringIO()

        @property
        def result(self):
            """"Retrieve filter result string."""
            return self._result

    def __init__(self):
        self._other = None

    def __or__(self, other):
        other._other = self
        return other

    def apply(self, result):
        """Apply this filter."""
        other = None
        if self._other:
            other = self._other.apply(result)
        return self.Result(self, result, other)


class ConsoleReport(ReportFilter):
    """Load a report from console."""

    class Result(ReportFilter.Result):
        """Result capsule"""

        @property
        def stream(self) -> TextIOBase:
            if self._result:
                return self._result.output
            return StringIO()


class FileReport(ReportFilter):
    """Load a report from a file."""

    class Result(ReportFilter.Result):
        """Result capsule"""

        @property
        @ReportFilter.Result.cached("_stream")
        def stream(self) -> TextIOBase:
            try:
                return open(self._report.filename, 'r', encoding='utf-8')
            except FileNotFoundError as e:
                raise RuntimeError from e

    def __init__(self, filename):
        super().__init__()
        self.filename = filename


class CropReport(ReportFilter):
    """Crop a report from a stream."""

    class Result(ReportFilter.Result):
        """Result capsule"""

        @property
        @ReportFilter.Result.cached("_stream")
        def stream(self) -> TextIOBase:
            dump = False
            istream = self._other.stream
            ostream = StringIO()
            istream.seek(0)
            for line in istream:
                if dump:
                    ostream.write(line)
                    if re.match(self._report.last, line):
                        break
                else:
                    if re.match(self._report.first, line):
                        dump = True
                        ostream.write(line)
            return ostream

    def __init__(self, first: AnyStr, last: AnyStr):
        super().__init__()
        self.first = first
        self.last = last


class TransformReport(ReportFilter):
    """Transform an XML report using XSLT."""

    class Result(ReportFilter.Result):
        """Result capsule"""

        @property
        @ReportFilter.Result.cached("_stream")
        def stream(self) -> TextIOBase:
            try:
                ostream = StringIO()
                istream = self._other.stream
                istream.seek(0)
                dom = etree.parse(istream)
                xslt = etree.parse(self._report.xslt)
                transform = etree.XSLT(xslt)
                newdom = transform(dom)
                ostream.write(etree.tostring(newdom, pretty_print=True).decode())
                return ostream
            except etree.XMLSyntaxError as e:
                raise RuntimeError from e

    def __init__(self, xslt):
        super().__init__()
        self.xslt = xslt


class JUnitReport(ReportFilter):
    """Capture a JUnit XML report."""

    class Result(ReportFilter.Result, ReportFilter.Summary):
        """Result capsule"""

        _junit_report = None

        def _update_title(self, title):
            new_title = self._report.title
            if isinstance(new_title, Callable):
                params = [title]
                if len(signature(new_title).parameters) >= 2:
                    params += [self._result]

                return new_title(*params)
            return new_title

        @property
        @ReportFilter.Result.cached("_junit_report")
        def junit_report(self) -> JUnitXml:
            """Load a JUnit format."""
            try:
                istream = self.stream
                istream.seek(0)
                report = JUnitXml.fromfile(istream)
                if self._report.title:
                    for testsuite in report:
                        testsuite.name = self._update_title(testsuite.name)
                return report
            except etree.XMLSyntaxError as e:
                raise RuntimeError from e

        @property
        def summary(self) -> Tuple[int, int]:
            report = self.junit_report
            executed = report.tests - report.skipped
            passed = executed - report.errors - report.failures
            return passed, executed

        def write(self, filename: AnyStr):
            self.junit_report.write(filename)

    def __init__(self, title: Optional[Union[AnyStr, Callable]] = None):
        super().__init__()
        self.title = title
