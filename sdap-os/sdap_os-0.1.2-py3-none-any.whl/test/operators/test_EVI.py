import unittest
from datetime import datetime
import xarray
import math
import numpy as np
from sdap.operators import EVI


class EVITestCase(unittest.TestCase):
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
            "time": [
                datetime.fromisoformat('2021-12-18'),
                datetime.fromisoformat('2021-12-19')
            ],
            "band": [1, 2]},
    )

    def test_consolidate(self):
        evi = EVI([1, 2, 3], [4, 5, 6])
        output1 = evi.tile_calc(self.input1['var'])
        output2 = evi.tile_calc(self.input2['var'])

        evi.consolidate([output1, output2])


    def test_tile_calc(self):

        evi = EVI([1, 2, 3], [4, 5, 6])

        output = evi.tile_calc(self.input1['var'])

        expected_result = [
            [
                [0.45454545, 0.37931034],
                [0.36170213, 0.35384615]
            ],
            [
                [0.34939759, 0.34653465],
                [0.34453782, 0.34306569]
            ]
        ]

        assert np.isclose(output.data, np.asarray(expected_result)).all()


if __name__ == '__main__':
    unittest.main()
