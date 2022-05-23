import datetime
import unittest

from py_dot.data import SummaryTimeUnit

from py_dot.data.frame import get_frame_from_series


class TestFrame(unittest.TestCase):

    def test_get_frame_from_iterator(self):
        self.assertListEqual(
            get_frame_from_series(
                series=[
                    [
                        datetime.datetime(2022, 11, 28),
                        1,
                        'foo'
                    ],
                    [
                        datetime.datetime(2022, 11, 28),
                        2,
                        'bar'
                    ],
                    [
                        datetime.datetime(2022, 11, 29),
                        3,
                        'baz'
                    ],
                    [
                        datetime.datetime(2022, 11, 29),
                        4,
                        'foo',
                    ],
                    [
                        datetime.datetime(2022, 11, 30),
                        5,
                        'bar'
                    ],
                    [
                        datetime.datetime(2022, 11, 30),
                        6,
                        'baz'
                    ],
                ],
                begin=datetime.datetime(2022, 11, 28),
                end=datetime.datetime(2022, 11, 30),
                unit=SummaryTimeUnit.date
            ),
            [
                ['Date', 'foo', 'bar', 'baz'],
                ['2022-11-28', 1, 2, 0],
                ['2022-11-29', 4, 0, 3],
                ['2022-11-30', 0, 5, 6]
            ]
        )
