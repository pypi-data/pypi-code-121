import pytest
import numpy as np

from cosapp.drivers.time.utils import TwoPointCubicInterpolator


@pytest.mark.parametrize("xs", [[1, 2], [0, 0.5], [-0.2, 0.1]])
@pytest.mark.parametrize("ys, dy", [
    ([0.7, -0.2], [-0.5, 0.1]),
    ([0, 1], [0, 1]),
    (   # 3D vector data
        [[-0.7, 0.1, 0.4], [1, -0.3, 0.2]],
        [[0.22, 1.4, 0.0], [0, 0.9, -0.6]],
    ),
])
def test_TwoPointCubicInterpolator(xs, ys, dy):
    xs = np.asarray(xs)
    ys = np.asarray(ys)
    dy = np.asarray(dy)
    f = TwoPointCubicInterpolator(xs, ys, dy)

    assert f(xs) == pytest.approx(np.transpose(ys), abs=1e-14)
