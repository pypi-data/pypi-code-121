# standard libraries
import logging
import math
import unittest

# third party libraries
# None

# local libraries
from nion.utils import Geometry


class TestGeometryClass(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_fit_to_size(self) -> None:
        eps = 0.0001
        rects = []
        sizes = []
        rects.append( ((0, 0), (300, 700)) )
        sizes.append( (600, 1200) )
        rects.append( ((0, 0), (300, 700)) )
        sizes.append( (1200, 600) )
        rects.append( ((0, 0), (600, 800)) )
        sizes.append( (700, 1300) )
        rects.append( ((0, 0), (600, 800)) )
        sizes.append( (1300, 700) )
        for rect, size in zip(rects, sizes):
            fit = Geometry.fit_to_size(rect, size)
            self.assertTrue(abs(float(fit[1][1])/float(fit[1][0]) - float(size[1])/float(size[0])) < eps)

    def test_int_point_ne(self) -> None:
        p1 = Geometry.IntPoint(x=0, y=1)
        p2 = Geometry.IntPoint(x=0, y=2)
        self.assertNotEqual(p1, p2)

    def test_rect_intersects(self) -> None:
        r1 = Geometry.IntRect.from_tlbr(10,10,20,30)
        r2 = Geometry.IntRect.from_tlbr(0, 15, 30, 25)
        self.assertTrue(r1.intersects_rect(r2))

    def test_ticker_produces_unique_labels(self) -> None:
        pairs = ((1, 4), (.1, .4), (1E12, 1.000062E12), (1E-18, 1.000062E-18), (-4, -1), (-10000.001, -10000.02),
                 (1E8 - 0.002, 1E8 + 0.002), (0, 1E8 + 0.002))

        for logarithmic in (False, True):
            for l, h in pairs:
                if not logarithmic or (l > 0 and h > 0):
                    with self.subTest(l=l, h=h, logarithmic=logarithmic):
                        ticker: Geometry.Ticker
                        if logarithmic:
                            ticker = Geometry.LogTicker(math.log10(l), math.log10(h))
                        else:
                            ticker = Geometry.LinearTicker(l, h)
                        self.assertEqual(len(set(ticker.labels)), len(ticker.labels))
            # print(ticker.labels)

    def test_linear_ticker_handles_edge_cases(self) -> None:
        self.assertEqual(Geometry.LinearTicker(0, 0).labels, ['0'])
        self.assertEqual(Geometry.LinearTicker(1, 1).labels, ['1'])
        self.assertEqual(Geometry.LinearTicker(-1, -1).labels, ['-1'])
        self.assertEqual(Geometry.LinearTicker(-math.inf, math.inf).labels, ['0'])
        self.assertEqual(Geometry.LinearTicker(-math.nan, math.nan).labels, ['0'])
        self.assertEqual(Geometry.LinearTicker(math.nan, 1).labels, ['0'])
        self.assertEqual(Geometry.LinearTicker(-math.inf, 1).labels, ['0'])
        self.assertEqual(Geometry.LinearTicker(0, math.inf).labels, ['0'])

    def test_log_ticker_handles_edge_cases(self) -> None:
        self.assertEqual(Geometry.LogTicker(0, 0, ticks=3).labels, ['1e+00', '1e+01'])
        self.assertEqual(Geometry.LogTicker(1, 1, ticks=3).labels, ['1e+01', '1e+02'])
        self.assertEqual(Geometry.LogTicker(-1, -1, ticks=3).labels, ['1e-01', '1e+00'])
        self.assertEqual(Geometry.LogTicker(-math.inf, math.inf).labels, ['0e+00'])
        self.assertEqual(Geometry.LogTicker(-math.nan, math.nan).labels, ['0e+00'])
        self.assertEqual(Geometry.LogTicker(math.nan, 1).labels, ['0e+00'])
        self.assertEqual(Geometry.LogTicker(-math.inf, 1).labels, ['0e+00'])
        self.assertEqual(Geometry.LogTicker(0, math.inf).labels, ['0e+00'])

    def test_ticker_produces_expected_labels(self) -> None:
        self.assertListEqual(list(Geometry.LinearTicker(0, 1e8, ticks=3).labels), ['0e+00', '5e+07', '1.0e+08'])
        self.assertListEqual(list(Geometry.LogTicker(0, 8, ticks=3).labels), ['1e+00', '1e+03', '1e+06', '1e+09'])
        self.assertListEqual(list(Geometry.LinearTicker(0, 1000, ticks=3).labels), ['0', '500', '1000'])
        self.assertListEqual(list(Geometry.LogTicker(0, 3, ticks=3).labels), ['1e+00', '1e+01', '1e+02', '1e+03'])
        self.assertListEqual(list(Geometry.LinearTicker(2e-18, 1.11252e-10, ticks=5).labels), ['0e+00', '5.0e-11', '1.0e-10', '1.50e-10'])
        self.assertListEqual(list(Geometry.LogTicker(math.log10(2e-18), math.log10(1.11252e-10), ticks=5).labels), ['1e-18', '1e-16', '1e-14', '1e-12', '1e-10', '1e-08'])
        self.assertListEqual(list(Geometry.LogTicker(math.log10(1E12), math.log10(1.000062E12), ticks=5).labels), ['1.00000e+12', '1.00002e+12', '1.00005e+12', '1.00007e+12'])
        self.assertListEqual(list(Geometry.LogTicker(math.log10(1E8 - 0.002), math.log10(1E8 + 0.002), ticks=3).labels), ['9.99999999977e+07', '1.00000000000e+08', '1.00000000002e+08'])

    def test_ticker_value_label(self) -> None:
        mn, mx = 18000000, 21000000
        ticker = Geometry.LinearTicker(mn, mx)
        self.assertIsNotNone(ticker.value_label(900000))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
