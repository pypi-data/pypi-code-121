import pytest

import numpy as np

from cosapp.core.numerics.boundary import TimeUnknown
from cosapp.core.eval_str import EvalString
from cosapp.systems import System
from cosapp.drivers.time.utils import TimeUnknownDict, TimeStepManager


class SubSystem(System):
    def setup(self):
        self.add_inward('x', 1.0)
        self.add_inward('y', np.ones(3))


class DummySystem(System):
    def setup(self):
        self.add_child(SubSystem('sub1'))
        self.add_child(SubSystem('sub2'))

        self.add_inward('f', 0.0)


@pytest.fixture(scope="function")
def system():
    return DummySystem("system")


@pytest.fixture(scope="function")
def unknowns(system):
    """Returns a list of dummy unknowns"""
    a = TimeUnknown(system, "f", der=0.5)
    b = TimeUnknown(system, "sub1.y", der="sub1.x")
    c = TimeUnknown(system, "sub2.x", der="sub1.y**2", max_time_step="0.1 * sub1.x")
    return a, b, c


@pytest.fixture(scope="function")
def unknown_dict(unknowns):
    a, b, c = unknowns
    return TimeUnknownDict(a=a, b=b, c=c)


@pytest.fixture(scope="function")
def manager(unknown_dict):
    return TimeStepManager(unknown_dict)


@pytest.mark.parametrize("data, expected", [
    (dict(), dict()),
    (dict(use_unknowns=True), dict()),
    (dict(use_unknowns=True, dt=None, max_growth_rate=2), dict(dt=None, max_growth_rate=2)),
    (dict(dt=0.01, max_growth_rate=1.7), dict(dt=0.01, max_growth_rate=1.7)),
    (dict(dt=0, max_growth_rate=1.5), dict(error=ValueError, mach="dt")),
    (dict(max_growth_rate=0.5), dict(error=ValueError, mach="max_growth_rate")),
    (dict(max_growth_rate=1), dict(error=ValueError, mach="max_growth_rate")),
    (dict(max_growth_rate=1), dict(error=ValueError, mach="max_growth_rate")),
    (dict(max_growth_rate=-0.2), dict(error=ValueError, mach="max_growth_rate")),
])
def test_TimeStepManager__init__(unknown_dict, data, expected):
    if data.pop('use_unknowns', False):  # use unknown_dict fixture?
        data.setdefault('transients', unknown_dict)
        expected['length'] = len(unknown_dict)
    else:
        expected.setdefault('length', 0)

    error = expected.get('error', None)

    if error is None:
        manager = TimeStepManager(**data)
        assert isinstance(manager.transients, TimeUnknownDict)
        assert len(manager.transients) == expected['length']
        assert manager.max_growth_rate > 1
        assert manager.max_growth_rate == expected.get('max_growth_rate', np.inf)
        assert manager.nominal_dt == expected.get('dt', None)
    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            TimeStepManager(**data)


@pytest.mark.parametrize("options, expected", [
    (dict(), dict(dt=0.3)),
    (dict(dt=0.1), dict(dt=0.1)),
    (dict(dt=0.01), dict(dt=0.01)),
])
def test_TimeStepManager_time_step(unknown_dict, options, expected):
    manager = TimeStepManager(unknown_dict, **options)

    s = manager.transients["a"].context
    s.sub1.x = 3
    s.sub1.y[:] = 1.2
    s.sub2.x = 0
    s.sub2.y[:] = 0

    assert manager.time_step() == pytest.approx(expected['dt'], rel=1e-14)


@pytest.mark.parametrize("options, prev_dt, expected", [
    (dict(dt=0.1), None, 0.1),
    (dict(dt=0.1), 0.01, 0.1),
    (dict(dt=0.1, max_growth_rate=2), None, 0.1),
    (dict(dt=0.1, max_growth_rate=2), 0.01, 0.02),
    (dict(dt=0.1, max_growth_rate=1.5), 0.01, 0.015),
    # Check that prev_dt is disregarded when prev_dt <= 0 or dt < prev_dt:
    (dict(dt=0.1, max_growth_rate=2), 0.5, 0.1),
    (dict(dt=0.1, max_growth_rate=2), -10, 0.1),
    (dict(dt=0.1, max_growth_rate=2), 0.0, 0.1),
])
def test_TimeStepManager_time_step_limited(unknowns, options, prev_dt, expected):
    x = unknowns[1]
    manager = TimeStepManager(TimeUnknownDict(x=x), **options)

    assert manager.time_step(prev_dt) == pytest.approx(expected, rel=1e-14)


@pytest.mark.parametrize("rate, expected", [
    (1.5, dict()),
    (2, dict()),
    (1 + 1e-6, dict(error=None)),
    # Erroneous values
    ("1.5", dict(error=TypeError)),
    (0, dict(error=ValueError)),
    (0.5, dict(error=ValueError)),
    (1, dict(error=ValueError)),
    (-1, dict(error=ValueError)),
    (-0.2, dict(error=ValueError)),
])
def test_TimeStepManager_max_growth_rate(manager, rate, expected):
    error = expected.get('error', None)

    if error is None:
        manager.max_growth_rate = rate
        assert manager.max_growth_rate == expected.get('rate', rate)
    else:
        with pytest.raises(error):
            manager.max_growth_rate = rate
