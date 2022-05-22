import unittest
import sys
import logging
import xarray
from sdap.data_access.drivers import S3COG
from sdap.data_access.index.spatial import Sentinel2Grid
from sdap.data_access.index.temporal import Daily
from sdap.operators import SpatialMean, EVI
import matplotlib.pyplot as plt
import time
from datetime import datetime

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

AWS_KEY='<your key here>'
AWS_SECRET='<your secret here>'

class S3COGTestCase(unittest.TestCase):

    def test_small_get(self):
        s3_cog_driver = S3COG(
            region_name='us-west-2',
            bucket='aqacf-nexus-stage',
            key_pattern=[
                'hls_cog/s1_output_latlon_HLS_L30_T{spatial_key}_{temporal_key}_cog.tif',
                'hls_cog/s1_output_latlon_HLS_S30_T{spatial_key}_{temporal_key}_cog.tif'
            ],
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
            spatial_index=Sentinel2Grid(),
            temporal_index=Daily(format="%Y%j")
        )

        lat_range = [42.303, 43.326]
        lon_range = [-71.572, -71.183]
        time_range_str = ['2017-05-20T00:00:00.000000+00:00', '2017-06-20T00:00:00.000000+00:00']
        time_range = [datetime.fromisoformat(t) for t in time_range_str]

        start = time.time()
        xas = s3_cog_driver.get_all(lon_range, lat_range, time_range, SpatialMean())
        print(f"performance: small mean request took {time.time() - start} s to average {xas.weight.sum().data.item()} observations")
        plt.figure()
        plt.plot(xas.time, xas['var'].data[0, 0, :, :])
        del xas
        plt.savefig('/tmp/small_mean.png')

        #plt.show()

    #TODO enable plot as a callback of the get all function, to be able to update a plot while data is fetched
    def plot_evi(self, results: xarray.DataArray):
        plt.figure()
        for x in results.x:
            for y in results.y:
                ts = results.sel({'x': x.values.item(), 'y': y.values.item()})
                plt.plot(ts.time, ts.variable, alpha=0.1)
        #plt.show()
        plt.savefig('/tmp/big_evi.png')

    def test_bigger_get(self):
        s3_cog_driver = S3COG(
            region='us-west-2',
            bucket='aqacf-nexus-stage',
            key_pattern=[
                'hls_cog/s1_output_latlon_HLS_L30_T{spatial_key}_{temporal_key}_cog.tif',
                'hls_cog/s1_output_latlon_HLS_S30_T{spatial_key}_{temporal_key}_cog.tif'
            ],
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
            spatial_index=Sentinel2Grid(),
            temporal_index=Daily(format="%Y%j")
        )

        lat_range = [42.1, 42.6]
        lon_range = [-72.0, -71.5]
        time_range = ['2017-01-01T00:00:00.000000+00:00', '2019-01-01T00:00:00.000000+00:00']
        time_range = [datetime.fromisoformat(t) for t in time_range]

        start = time.time()
        xas = s3_cog_driver.get_all(lon_range, lat_range, time_range, SpatialMean())
        print(f"performance: bigger mean request took {time.time() - start} s to average {xas.weight.sum().data.item()} observations")

        plt.figure()
        plt.plot(xas.time, xas['var'].data[0,0,:,:])
        del xas
        plt.savefig('/tmp/big_mean.png')

        #plt.show()

    def test_bigger_get_evi(self):
        s3_cog_driver = S3COG(
            region='us-west-2',
            bucket='aqacf-nexus-stage',
            key_pattern=[
                'hls_cog/s1_output_latlon_HLS_L30_T{spatial_key}_{temporal_key}_cog.tif',
                'hls_cog/s1_output_latlon_HLS_S30_T{spatial_key}_{temporal_key}_cog.tif'
            ],
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
            spatial_index=Sentinel2Grid(),
            temporal_index=Daily(format="%Y%j")
        )

        lat_range = [42.5, 42.6]
        lon_range = [-71.6, -71.5]
        time_range = ['2017-01-01T00:00:00.000000+00:00', '2019-01-01T00:00:00.000000+00:00']
        time_range = [datetime.fromisoformat(t) for t in time_range]

        evi = EVI(numerator_coeff=[0, 0, -2.5, 2.5, 0, 0, 0],
                  denominator_coeff=[0, 0, 2.4, 1, 0, 0, 1])

        start = time.time()
        xas = s3_cog_driver.get_all(lon_range, lat_range, time_range, evi)
        n_results = len(xas.x)*len(xas.y)*len(xas.time)
        print(f"performance: evi request took {time.time() - start} s for {n_results} points")

        self.plot_evi(xas)
        del xas


if __name__ == '__main__':
    unittest.main()
