from numbers import Real
from typing import Tuple

from wai.test import AbstractTest
from wai.test.decorators import Test, SubjectArgs

from wai.common import Interval


class IntervalTest(AbstractTest):
    """
    Tests the Interval class.
    """
    @classmethod
    def subject_type(cls):
        return Interval

    def standard_point_test(self, subject: Interval, *points: Tuple[Real, bool]):
        for value, should_succeed in points:
            with self.subTest(value=value):
                if should_succeed:
                    self.assertIn(value, subject, f"{value} should be in {subject}")
                else:
                    self.assertNotIn(value, subject, f"{value} should not be in {subject}")

    @Test
    @SubjectArgs(0, 1)
    def standard_interval(self, subject: Interval):
        self.standard_point_test(subject,
                                 (-0.5, False),
                                 (0.0, True),
                                 (0.5, True),
                                 (1.0, False),
                                 (1.5, False))

    @Test
    @SubjectArgs(0, None, upper_inclusive=True)
    def open_upper_interval(self, subject: Interval):
        self.standard_point_test(subject,
                                 (-0.5, False),
                                 (0.0, True),
                                 (0.5, True),
                                 (1.0, True),
                                 (1.5, True))

    @Test
    @SubjectArgs(None, 1)
    def open_lower_interval(self, subject: Interval):
        self.standard_point_test(subject,
                                 (-0.5, True),
                                 (0.0, True),
                                 (0.5, True),
                                 (1.0, False),
                                 (1.5, False))

    @Test
    @SubjectArgs(1, 0)
    def outside_interval(self, subject: Interval):
        self.standard_point_test(subject,
                                 (-0.5, True),
                                 (0.0, False),
                                 (0.5, False),
                                 (1.0, True),
                                 (1.5, True))

    @Test
    @SubjectArgs(0, 0, True, True)
    def point_interval(self, subject: Interval):
        self.standard_point_test(subject,
                                 (-0.5, False),
                                 (0.0, True),
                                 (0.5, False),
                                 (1.0, False),
                                 (1.5, False))

    @Test
    @SubjectArgs(0, 0, False)
    def exclude_point_interval(self, subject: Interval):
        self.standard_point_test(subject,
                                 (-0.5, True),
                                 (0.0, False),
                                 (0.5, True),
                                 (1.0, True),
                                 (1.5, True))

    @Test
    @SubjectArgs(0, 0, False)
    def static_creators(self, subject: Interval):
        for interval, test in {(Interval.total(), Interval.is_total),
                               (Interval.empty(), Interval.is_empty),
                               (Interval.open_lower(0), Interval.is_open_lower),
                               (Interval.open_upper(0), Interval.is_open_upper),
                               (Interval.singular(0), Interval.is_singular),
                               (Interval.exclude_value(0), Interval.is_exclude_value),
                               (Interval.inside(1, 0), Interval.is_inside),
                               (Interval.outside(0, 1), Interval.is_outside)}:
            with self.subTest(test=test.__name__):
                self.assertTrue(test(interval))

    @Test
    @SubjectArgs(0, 0, False)
    def to_string(self, subject: Interval):
        for interval, expected in {(Interval.total(), "[:]"),
                                   (Interval.empty(), "(:)"),
                                   (Interval.open_lower(0, True), "[:0]"),
                                   (Interval.open_upper(0, False), "(0:]"),
                                   (Interval.singular(0), "[0]"),
                                   (Interval.exclude_value(0), "(0)"),
                                   (Interval.inside(1, 0), "[0:1)"),
                                   (Interval.outside(0, 1, False, True), "0](1")}:
            with self.subTest(expected=expected):
                self.assertEqual(str(interval), expected)
