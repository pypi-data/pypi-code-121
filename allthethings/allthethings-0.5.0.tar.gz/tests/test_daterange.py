import datetime
import unittest
from typing import List

from allthethings.daterange import DateRange
from allthethings.dates import read_date


class TestDateRange(unittest.TestCase):

    def test_date_cmp(self):
        d1 = read_date('2020-04-01')
        d2 = read_date('2020-04-01')
        d3 = read_date('2020-04-02')
        self.assertTrue(d1 <= d2)
        self.assertFalse(d1 < d2)
        self.assertTrue(d1 < d3)

    def test_date_range_no_bounds(self):
        d = DateRange("..")
        self.assertEqual(None, d.min)
        self.assertEqual(None, d.max)

    def test_date_range_contains(self):
        d = DateRange('2020-04-01,2020-05-01..2020-05-20,2020-06-01..')
        self.assertTrue('2019-03-31' not in d)
        self.assertTrue('2020-03-31' not in d)
        self.assertTrue('2020-04-01' in d)
        self.assertTrue('2020-04-02' not in d)
        self.assertTrue('2020-05-01' in d)
        self.assertTrue('2020-05-10' in d)
        self.assertTrue('2020-05-20' in d)
        self.assertTrue('2020-05-21' not in d)
        self.assertTrue('2020-06-01' in d)
        self.assertTrue('2020-06-02' in d)
        self.assertTrue('2021-06-02' in d)

    def test_date_range_min_max(self):
        d = DateRange('2020-04-01,2020-05-01..2020-05-20,2020-06-01..')
        self.assertEqual(read_date('2020-04-01'), d.min)
        self.assertEqual(None, d.max)
        d = DateRange('2020-04-01,2020-05-01..2020-05-20,2020-06-01..,2019-01-01')
        self.assertEqual(read_date('2019-01-01'), d.min)
        self.assertEqual(None, d.max)
        d = DateRange('2020-04-01,2020-05-01..2020-05-20,2020-06-01..2020-06-15,2019-01-01')
        self.assertEqual(read_date('2019-01-01'), d.min)
        self.assertEqual(read_date('2020-06-15'), d.max)
        d = DateRange('2020-04-01,2020-05-01..2020-05-20,2031-03-15,2020-06-01..2020-06-15,..2019-01-01')
        self.assertEqual(None, d.min)
        self.assertEqual(read_date('2031-03-15'), d.max)

    def test_date_range_iter(self):
        d = DateRange('2020-01-01..2020-01-04')
        self.assertEqual([
            read_date('2020-01-01'),
            read_date('2020-01-02'),
            read_date('2020-01-03'),
            read_date('2020-01-04'),
        ], [*iter(d)])
        d = DateRange('2020-01-01..')
        self.assertEqual([
            read_date('2020-01-01'),
            read_date('2020-01-02'),
            read_date('2020-01-03'),
        ], [*d.iter(upper='2020-01-03')])

    def test_date_range_months(self):
        d = DateRange('2021-02')
        self.assertEqual(28, len([*d]))
        d = DateRange('2020-02')
        self.assertEqual(29, len([*d]))
        d = DateRange('2020-12')
        self.assertEqual(31, len([*d]))

    def test_date_range_month_bounds(self):
        d = DateRange('2020-01..2020-12')
        self.assertEqual(read_date('2020-01-01'), d.min)
        self.assertEqual(read_date('2020-12-31'), d.max)

    def test_date_range_itermonths(self):
        ranges: List[DateRange] = [*DateRange('2020-01..2020-12').itermonths()]
        self.assertEqual(12, len(ranges))
        for month, date_range in enumerate(ranges, start=1):
            self.assertEqual(1, date_range.min.day)
            self.assertEqual(month, date_range.min.month)
            self.assertEqual(month, date_range.max.month)

    def test_date_range_timedelta(self):
        def today():
            return datetime.datetime.utcnow().date()

        dr = DateRange('2020-01..DAYS(31)')
        self.assertEqual(dr.min, read_date('2020-01-01'))
        self.assertEqual(dr.max, read_date('2020-02-01'))
        dr = DateRange('DAYS(31)..2020-01')
        self.assertEqual(dr.min, read_date('2019-12-01'))
        self.assertEqual(dr.max, read_date('2020-01-01'))
        dr = DateRange('DAYS(31)..today')
        self.assertEqual(dr.min, read_date((today() - datetime.timedelta(days=31)).isoformat()))
        self.assertEqual(dr.max, read_date(today().isoformat()))
        dr = DateRange('today..DAYS(31)')
        self.assertEqual(dr.min, read_date(today().isoformat()))
        self.assertEqual(dr.max, read_date((today() + datetime.timedelta(days=31)).isoformat()))

    def test_date_comparison(self):
        r1 = DateRange('..2021-08-01')

        self.assertTrue(read_date('2021-07-01') <= r1)
        self.assertTrue(read_date('2021-07-01') >= r1)
        self.assertFalse(read_date('2021-07-01') < r1)
        self.assertFalse(read_date('2021-07-01') > r1)

        self.assertTrue(read_date('2021-08-01') <= r1)
        self.assertTrue(read_date('2021-08-01') >= r1)
        self.assertFalse(read_date('2021-08-01') < r1)
        self.assertFalse(read_date('2021-08-01') > r1)

        self.assertFalse(read_date('2021-08-02') <= r1)
        self.assertTrue(read_date('2021-08-02') >= r1)
        self.assertFalse(read_date('2021-08-02') < r1)
        self.assertTrue(read_date('2021-08-02') > r1)

        r2 = DateRange('2020-07-01..2020-08-01')

        self.assertTrue(read_date('2020-06-01') <= r2)
        self.assertFalse(read_date('2020-06-01') >= r2)
        self.assertTrue(read_date('2020-06-01') < r2)
        self.assertFalse(read_date('2020-06-01') > r2)

        self.assertTrue(read_date('2020-07-01') <= r2)
        self.assertTrue(read_date('2020-07-01') >= r2)
        self.assertFalse(read_date('2020-07-01') < r2)
        self.assertFalse(read_date('2020-07-01') > r2)

        self.assertTrue(read_date('2020-08-01') <= r2)
        self.assertTrue(read_date('2020-08-01') >= r2)
        self.assertFalse(read_date('2020-08-01') < r2)
        self.assertFalse(read_date('2020-08-01') > r2)

        self.assertFalse(read_date('2020-08-02') <= r2)
        self.assertTrue(read_date('2020-08-02') >= r2)
        self.assertFalse(read_date('2020-08-02') < r2)
        self.assertTrue(read_date('2020-08-02') > r2)

        r3 = DateRange('2019-08-01..')

        self.assertTrue(read_date('2019-07-01') <= r3)
        self.assertFalse(read_date('2019-07-01') >= r3)
        self.assertTrue(read_date('2019-07-01') < r3)
        self.assertFalse(read_date('2019-07-01') > r3)

        self.assertTrue(read_date('2019-08-01') <= r3)
        self.assertTrue(read_date('2019-08-01') >= r3)
        self.assertFalse(read_date('2019-08-01') < r3)
        self.assertFalse(read_date('2019-08-01') > r3)

        self.assertTrue(read_date('2019-08-02') <= r3)
        self.assertTrue(read_date('2019-08-02') >= r3)
        self.assertFalse(read_date('2019-08-02') < r3)
        self.assertFalse(read_date('2019-08-02') > r3)

    def test_empty_daterange(self):
        dr = DateRange()
        i = 0
        for d in dr:
            i += 1
        self.assertEqual(0, i)
        self.assertFalse(datetime.date(2020, 1, 1) in dr)

    def test_one_day_range(self):
        dr = DateRange("2020-01-01..2020-01-01")
        self.assertEqual([datetime.date(2020, 1, 1)], [*dr])


if __name__ == '__main__':
    unittest.main()
