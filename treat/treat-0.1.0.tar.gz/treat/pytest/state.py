from collections import defaultdict
from typing import Dict
from typing import Iterator
from typing import Tuple

from .test_result import TestResult


class State:
    def __init__(self, group: Tuple[str]) -> None:
        self.suite_total_tests = None
        self._suite_tests = {}
        self._group = group
        self._group_tests: Dict[str, TestResult] = {}
        self._parameter_sets = defaultdict(dict)

    @property
    def group(self) -> Tuple[str]:
        return self._group

    @property
    def tests(self) -> Iterator[TestResult]:
        return self._group_tests.values()

    @property
    def group_title(self) -> str:
        if any(test.type == TestResult.FAIL for test in self._group_tests.values()):
            return "FAIL"

        if any(test.type != TestResult.PASS for test in self._group_tests.values()):
            return "WARN"

        return "PASS"

    @property
    def group_title_color(self) -> str:
        if any(test.type == TestResult.FAIL for test in self._group_tests.values()):
            return "red"

        if any(test.type != TestResult.PASS for test in self._group_tests.values()):
            return "yellow"

        return "green"

    @property
    def group_tests_count(self) -> int:
        return len(self._group_tests)

    @property
    def suite_tests_count(self) -> int:
        count = 0
        for group_tests in self._suite_tests.values():
            for _ in group_tests.values():
                count += 1

        return count

    def parameter_set(self, test) -> int:
        return self._parameter_sets[test.base_identifier][test.identifier]

    def add(self, test: TestResult) -> None:
        if test.identifier not in self._group_tests:
            self._group_tests[test.identifier] = test
        else:
            current_test = self._group_tests[test.identifier]
            if current_test.type != test.type:
                if test.type == TestResult.FAIL:
                    self._group_tests[test.identifier] = test

        if self._group not in self._suite_tests:
            self._suite_tests[self._group] = {}

        self._suite_tests[self._group] = self._group_tests

    def test_exists_in_group(self, test: TestResult) -> bool:
        return test.identifier in self._group_tests

    def group_has_changed(self, test: TestResult) -> bool:
        return tuple(test.identifier.split("::")[:-1]) != self._group

    def move_to(self, test: TestResult) -> None:
        self._group = tuple(test.identifier.split("::")[:-1])
        self._group_tests = {}

    def count_tests_in_suite_with_type(self, type: str) -> int:
        count = 0

        for group_tests in self._suite_tests.values():
            for test in group_tests.values():
                if test.type == type:
                    count += 1

        return count

    def add_parameter_set_for(self, test: TestResult) -> None:
        if test.parameters:
            if test.identifier not in self._parameter_sets[test.base_identifier]:
                self._parameter_sets[test.base_identifier][test.identifier] = (
                    len(self._parameter_sets[test.base_identifier]) + 1
                )
