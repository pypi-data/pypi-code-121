import pytest
import numpy as np

from cosapp.drivers.time.scenario import TimeAssignString
from .conftest import ScalarOde, VectorOde


def test_TimeAssignString__init__():
    ode = ScalarOde('ode')
    interpolator = lambda t: t if t < 1 else 3 - 2 * t
    bc = TimeAssignString('df', interpolator, ode)
    bc_locals = bc.locals
    assert len(bc_locals.keys()) == 3
    assert "t" in bc_locals
    assert "ode" in bc_locals
    assert bc_locals["ode"] is ode

    with pytest.raises(TypeError, match="must be a callable function"):
        TimeAssignString('df', 0.5, ode)


def test_TimeAssignString_scalar_exec(clock):
    ode = ScalarOde('ode')
    interpolator = lambda t: t if t < 1 else 3 - 2 * t
    bc = TimeAssignString('df', interpolator, ode)

    # Check `exec` with no argument: synched with system time
    for clock.time in (0, 0.8, 1, 2, 3.4):
        bc.exec()
        assert ode.df == interpolator(clock.time)
        assert bc.locals['t'] == ode.time

    # Check `exec` with prescribed time
    clock.time = 999

    for t in (0, 0.8, 1, 2, 3.4):
        bc.exec(t)
        assert ode.df == interpolator(t)
        assert ode.time == clock.time
        assert bc.locals['t'] == t


def test_TimeAssignString_vector_exec(clock):
    ode = VectorOde('ode')
    interpolator = lambda t: np.array([t, np.exp(-t), np.sin(t)])
    bc = TimeAssignString('dv', interpolator, ode)

    # Check `exec` with no argument: synched with system time
    for clock.time in (0, 0.8, 1, 2, 3.4, -2.5):
        bc.exec()
        assert ode.dv == pytest.approx(interpolator(clock.time), abs=0)
        assert bc.locals['t'] == ode.time

    # Check `exec` with prescribed time
    clock.time = 999

    for t in (0, 0.8, 1, 2, 3.4, -2.5):
        bc.exec(t)
        assert ode.dv == pytest.approx(interpolator(t), abs=0)
        assert ode.time == clock.time
        assert bc.locals['t'] == t
