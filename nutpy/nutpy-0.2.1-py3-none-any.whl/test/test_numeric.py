import numpy as np
from numpy.testing import assert_allclose

from nutpy import numeric as nm


def test_perpendicular_vector():
    """
    Test perpendicular_vector function
    """
    u = np.random.random((3, 1))

    v = nm.perpendicular_vector(u)

    s = v.T @ u

    assert_allclose(s, 0., rtol=0, atol=1e-12)
