import inspect

from ._method import TestMethod
from ._wrappers import TEST_METHOD_NAME

from typing import Dict, List

from collections import OrderedDict


class TestGroup:
    def __init__(self, name, classTest, coverage: bool = False):
        self.coverage = coverage
        self.name = name
        self.classTest = classTest
        self.tests: OrderedDict[str, TestMethod] = OrderedDict()
        self.category = classTest.category
        if self.category == "":
            self.category = classTest.__module__.split(".")[-1].capitalize()

        tests = {}
        for method_name, method in inspect.getmembers(classTest):
            if "__" in method_name:
                continue
            if not inspect.isfunction(method):
                continue
            if not hasattr(classTest, method.__name__):
                continue

            a, j = method.__annotations__, method.__dict__
            method_name = method.__name__
            qual_name = method.__qualname__
            if method_name == TEST_METHOD_NAME or TEST_METHOD_NAME in qual_name:
                test_function = TestMethod(
                    classTest,
                    method_name,
                    method,
                    self.category,
                    self.name,
                    **method.__dict__,
                )

                tests[test_function.name] = test_function

        sorted_tests = dict(
            sorted(tests.items(), key=lambda item: item[1].func.__code__.co_firstlineno)
        )
        self.tests = sorted_tests

    def get_from_database(self):
        for test in self.tests.values():
            test.get_from_database()

    def test(self, name: str):
        if name in self.tests:
            self.tests[name].test(coverage=self.coverage)

    def test_all(self, names: List[str] = []):
        if len(names) == 0:
            classTest = self.classTest()
            for method in self.tests.values():
                method.test(classTest=classTest, coverage=self.coverage)
        else:
            for name in names:
                if name in self.tests:
                    self.tests[name].test(coverage=self.coverage)

    def save_all(self):
        for method in self.tests.values():
            method.save()

    def get_tests_names(self):
        return list(self.tests.keys())

    def print(self, output=True):
        txt = ""
        for test_name, test_def in self.tests.items():
            txt += "{:60} {:4}".format(test_name, test_def.print()) + "\n"
        if output:
            print(txt)
        return txt

    def to_json(self):
        tests = self.tests
        return tests
