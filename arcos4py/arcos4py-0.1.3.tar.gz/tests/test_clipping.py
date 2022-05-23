import numpy as np

from arcos4py.tools import clipMeas


def test_clipping():
    data = np.linspace(1, 10, 10).astype(int)
    out = clipMeas(data).clip(0.3, 0.7)
    true_val = np.array([3.7, 3.7, 3.7, 4.0, 5.0, 6.0, 7.0, 7.3, 7.3, 7.3])
    np.testing.assert_almost_equal(out, true_val)
