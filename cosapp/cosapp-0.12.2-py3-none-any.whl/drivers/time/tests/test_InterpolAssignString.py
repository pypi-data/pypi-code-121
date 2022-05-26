import pytest

from cosapp.drivers.time.scenario import Interpolator, InterpolAssignString
from .conftest import ScalarOde


@pytest.fixture(scope='function')
def ode():
    return ScalarOde('ode')


@pytest.fixture(scope='function')
def data():
    return [[0, 0], [1, 1], [10, -17]]


def test_InterpolAssignString__init__(ode, data):
    interpolator = Interpolator(data)
    bc = InterpolAssignString('df', interpolator, ode)
    assert str(bc) == "df = Interpolator(t)"
    bc_locals = bc.locals
    assert len(bc_locals.keys()) == 3
    assert "t" in bc_locals
    assert "ode" in bc_locals
    assert bc_locals["ode"] is ode


def test_InterpolAssignString_error(ode, data):
    message = "Functions used in time boundary conditions may only be of type `Interpolator`"

    with pytest.raises(TypeError, match=message):
        InterpolAssignString('df', lambda t: 2 * t, ode)

    class CustomInterpolator(Interpolator):
        def __init__(self, data):
            super().__init__(data)
    
    with pytest.raises(TypeError, match=message):
        InterpolAssignString('df', CustomInterpolator(data), ode)


def test_InterpolAssignString_exec(ode, data, clock):
    interpolator = Interpolator(data)
    bc = InterpolAssignString('df', interpolator, ode)
    ode.df = 0.123
    clock.time = 0
    bc.exec()
    assert ode.df == 0
    clock.time = 0.5
    bc.exec()
    assert ode.df == pytest.approx(0.5, rel=1e-15)
    clock.time = 2
    bc.exec()
    assert ode.df == pytest.approx(-1, rel=1e-15)

    for clock.time in (0, 0.8, 1, 2, 3.4):
        bc.exec()
        assert ode.df == interpolator(clock.time)
        assert bc.locals['t'] == ode.time
