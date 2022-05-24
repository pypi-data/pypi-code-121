import datetime
import unittest

from allthethings.ranges import range_incl, range_excl


class RangesTestCase(unittest.TestCase):

    def test_range_incl_with_dates(self):
        ds = list(range_incl(datetime.date(2020, 2, 27), datetime.date(2020, 3, 2)))
        self.assertEqual([
            datetime.date(2020, 2, 27),
            datetime.date(2020, 2, 28),
            datetime.date(2020, 2, 29),
            datetime.date(2020, 3, 1),
            datetime.date(2020, 3, 2),
        ], ds)

    def test_range_excl_with_dates(self):
        ds = list(range_excl(datetime.date(2020, 2, 27), datetime.date(2020, 3, 2)))
        self.assertEqual([
            datetime.date(2020, 2, 27),
            datetime.date(2020, 2, 28),
            datetime.date(2020, 2, 29),
            datetime.date(2020, 3, 1),
        ], ds)

    def test_range_incl_with_dates_step(self):
        ds = list(range_incl(datetime.date(2020, 2, 27), datetime.date(2020, 3, 2), step=2))
        self.assertEqual([
            datetime.date(2020, 2, 27),
            datetime.date(2020, 2, 29),
            datetime.date(2020, 3, 2),
        ], ds)

    def test_range_excl_with_dates_step(self):
        ds = list(range_excl(datetime.date(2020, 2, 27), datetime.date(2020, 3, 2), step=2))
        self.assertEqual([
            datetime.date(2020, 2, 27),
            datetime.date(2020, 2, 29),
        ], ds)


if __name__ == '__main__':
    unittest.main()
