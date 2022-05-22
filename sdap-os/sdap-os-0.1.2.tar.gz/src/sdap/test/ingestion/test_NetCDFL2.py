import unittest
from sdap.ingestion import NetCDFL2
from sdap.data_access.index.spatial import GoogleS2
from sdap.data_access.index.temporal import Daily



class NetCDFL2TestCase(unittest.TestCase):

    def test_create_tiles(self):
        file_path = '/Users/loubrieu/Documents/sdap/tropomi.gesdisc.eosdis.nasa.gov/data/S5P_TROPOMI_Level2/S5P_L2__NO2____HiR.1/2021/001/S5P_OFFL_L2__NO2____20201231T234906_20210101T013036_16679_01_010400_20210102T163556.nc'
        spatial_index = GoogleS2(level=3)
        temporal_index = Daily(format="%Y%j")
        granule = NetCDFL2(file_path,
                           spatial_index,
                           temporal_index,
                           group='PRODUCT'
                           )

        for tile in granule.get_tiles():
            pass

        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
