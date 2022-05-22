import unittest
from sdap.data_access.index.spatial import Sentinel2Grid

class Sentinel2GridTestCase(unittest.TestCase):
    def test_get_codes(self):
        lat_range = [42.3, 42.35]
        lon_range = [-71.34, -71.22]

        #lat_range = [42.303, 43.326]
        #lon_range = [-72.572, -71.183]

        i = Sentinel2Grid()
        s2_codes = i.get_codes(lon_range, lat_range, 'epsg:4326')

        assert s2_codes == ['18TYM', '18TYN', '19TBG', '19TCG', '19TCH']  # add assertion here


if __name__ == '__main__':
    unittest.main()
