import pytest
import numpy as np

from cosapp.drivers.time.scenario import Interpolator


@pytest.fixture(scope='function')
def data():
    return [[0, 0], [1, 1], [10, -17]]


@pytest.mark.parametrize("kind", Interpolator.Kind)
@pytest.mark.parametrize("data, expected", [
    ([[0, 1, 10], [0, 1, -17]], dict()),
    ([[0, 0], [1, 1]], dict(data=[[0, 1], [0, 1]])),
    ([[0, 0], [1, 1], [10, -17]], dict(data=[[0, 1, 10], [0, 1, -17]])),
    ([(0, 0), (1, 1), (10, -17)], dict(data=[[0, 1, 10], [0, 1, -17]])),
    ([[0], [1, 1], [10, -17]], dict(error=ValueError)),
    ([[0, 1, 2], [1, 2, 5, -17]], dict(error=ValueError)),
    ([[0, 0]], dict(error=ValueError)),
    ("foobar", dict(error=ValueError)),
    (dict(x=[0, 1], y=[1, 0.3]), dict(error=TypeError)),
])
def test_Interpolator__init__(data, kind, expected):
    error = expected.get('error', None)

    if error is None:
        interpolator = Interpolator(data, kind)
        assert interpolator.kind is kind
        assert np.array_equal(interpolator.data, expected.get('data', data))
    else:
        with pytest.raises(error, match=expected.get('match', None)):
            Interpolator(data, kind)


@pytest.mark.parametrize("kind, points, expected", [
    (Interpolator.Kind.Linear, [0, 0.5, 1, 2, 5.5], [0, 0.5, 1, -1, -8]),  # F(x) = x if x < 1 else 3 - 2 * x
    (Interpolator.Kind.CubicSpline, [0, 0.5, 1, 2, 5.5], [0, 0.575, 1, 1.4, -1.925]),
    (Interpolator.Kind.Pchip, [0, 0.5, 1, 2, 5.5], [0, 0.6625, 1, 0.84691358, -2.7125]),
])
def test_Interpolator__call__(kind, data, points, expected):
    interpolator = Interpolator(data, kind)
    assert interpolator(points) ==  pytest.approx(expected, rel=1e-8)


def test_Interpolator_kind(data):
    interpolator = Interpolator(data)
    points = [0, 0.5, 1, 2, 5.5]

    interpolator.kind = Interpolator.Kind.Linear
    assert interpolator.kind is Interpolator.Kind.Linear
    assert interpolator(points) ==  pytest.approx([0, 0.5, 1, -1, -8], rel=1e-15)

    interpolator.kind = Interpolator.Kind.CubicSpline
    assert interpolator.kind is Interpolator.Kind.CubicSpline
    assert interpolator(points) ==  pytest.approx([0, 0.575, 1, 1.4, -1.925], rel=1e-15)

    interpolator.kind = Interpolator.Kind.Pchip
    assert interpolator.kind is Interpolator.Kind.Pchip
    assert interpolator(points) ==  pytest.approx([0, 0.6625, 1, 0.84691358, -2.7125], rel=1e-8)
