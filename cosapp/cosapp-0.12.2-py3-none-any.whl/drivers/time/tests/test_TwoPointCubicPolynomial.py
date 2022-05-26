import pytest
import numpy as np

from cosapp.drivers.time.utils import TwoPointCubicPolynomial


@pytest.mark.parametrize("xs", [[1, 2], [0, 0.5], [-0.2, 0.1]])
@pytest.mark.parametrize("ys", [[0.7, -0.2], [0, 1]])
@pytest.mark.parametrize("dy", [[-0.5, 0.1], [0, 1], [0, 0]])
def test_TwoPointCubicPolynomial(xs, ys, dy):
    xs = np.asarray(xs)
    ys = np.asarray(ys)
    dy = np.asarray(dy)
    p = TwoPointCubicPolynomial(xs, ys, dy)
    dp = p.deriv()

    assert p.degree() == 3
    assert p(xs) == pytest.approx(ys, abs=1e-14)
    assert dp(xs) == pytest.approx(dy, abs=1e-14)


def test_numpy_polynomial():
    p = np.polynomial.Polynomial([0, 1], [1, 2], [0, 1])

    assert p(0) == pytest.approx(-1, abs=1e-14)
    assert p(2) == pytest.approx(+1, abs=1e-14)
