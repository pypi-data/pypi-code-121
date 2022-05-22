import unittest
from sdap.data_access.index.spatial import MGRS


class MGRSTestCase(unittest.TestCase):
    def test_get_single_codes(self):
        lat_range = [42.3, 42.35]
        lon_range = [-71.34, -71.22]

        #lat_range = [42.303, 43.326]
        #lon_range = [-72.572, -71.183]

        m = MGRS(level=5)
        mgrs_codes = m.get_codes(lon_range, lat_range)

        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
