# -*- coding: utf-8 -*-

import unittest
import mud_examples.linear.models as mdr
import numpy as np

__author__ = "Mathematical Michael"
__copyright__ = "Mathematical Michael"
__license__ = "mit"


class TestRandomSetups(unittest.TestCase):
    def test_random_map(self):
        for d in ["normal", "uniform", None]:
            for r in [True, False]:
                for _dim_in in [1, 5, 10]:
                    A = mdr.createRandomLinearMap(
                        dim_input=_dim_in, dim_output=10, dist=d, repeated=r
                    )
                    assert A is not None
                    if not r:
                        assert np.linalg.matrix_rank(A) == _dim_in
                    else:
                        assert np.linalg.matrix_rank(A) == 1
