import unittest
import xarray
import numpy as np
from datetime import datetime

from sdap.operators import SpatialMean


class SpatialMeanTestCase(unittest.TestCase):
    input1 = xarray.Dataset(
        {
            "var": (
                ("x", "y", "time", "band"),
                np.arange(16).reshape(2, 2, 2, 2),
            )
        },
        coords={
            "x": [10, 20],
            "y": [150, 160],
            "request_x": (('x'), [30, 40]),
            "request_y": (('y'), [150, 160]),
            "time": [
                datetime.fromisoformat('2021-12-16'),
                datetime.fromisoformat('2021-12-17')
            ],
            "band": [1, 2]},
    )

    input2 = xarray.Dataset(
        {
            "var": (
                ("x", "y", "time", "band"),
                np.arange(16, 32).reshape(2, 2, 2, 2),
            )
        },
        coords={
            "x": [30, 40],
            "y": [150, 160],
            "request_x": (('x'), [30, 40]),
            "request_y": (('y'), [150, 160]),
            "time": [
                datetime.fromisoformat('2021-12-18'),
                datetime.fromisoformat('2021-12-19')
            ],
            "band": [1, 2]},
    )

    def test_tile_calc(self):

        spatial_mean = SpatialMean()
        result = spatial_mean.tile_calc(self.input1['var'])

        assert (result['var'].data == [[6., 7.],[8., 9.]]).all()

    def test_consolidate(self):
        spatial_mean = SpatialMean()
        mean1 = spatial_mean.tile_calc(self.input1['var'])
        mean2 = spatial_mean.tile_calc(self.input2['var'])

        consolidated_mean = spatial_mean.consolidate([mean1, mean2])


if __name__ == '__main__':
    unittest.main()
