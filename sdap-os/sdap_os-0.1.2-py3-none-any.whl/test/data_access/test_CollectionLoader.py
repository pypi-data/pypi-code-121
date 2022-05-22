import unittest
import os
from sdap.data_access import CollectionLoader
from sdap.operators import SpatialMean


class CollectionLoaderTestCase(unittest.TestCase):

    def test_collectionLoad(self):

        collection_config_file = 'collection-config.yaml'
        secret_file = 'secrets.yaml'
        collection_config_dir = os.path.dirname(__file__)

        collection_loader = CollectionLoader(
            os.path.join(collection_config_dir, collection_config_file),
            secret_file=os.path.join(collection_config_dir, secret_file)
            )

        lat_range = [42.303, 43.326]
        lon_range = [-71.272, -71.183]
        time_range = ['2017-05-20T00:00:00.000000+00:00', '2017-06-20T00:00:00.000000+00:00']

        collection_loader.get_driver('hls').get(lon_range, lat_range, time_range, operator=SpatialMean())


if __name__ == '__main__':
    unittest.main()
