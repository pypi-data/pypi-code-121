import pytest

import numpy as np

from cosapp.systems import System
from cosapp.drivers.time.utils import TimeVarManager
from cosapp.core.numerics.basics import MathematicalProblem
from .conftest import (
    ScalarOde, VectorOde,
    PointMass, PointMassWithPorts,
    ExpRampOde, DampedMassSpring,
    CoupledTanks,
    )


@pytest.mark.parametrize("ders, expected", [
    ({}, {}),
    ({'h': 'Q / A'}, {'h': ['h', 'Q / A']}),
    ({'x': 'v'}, {'x': ['x', 'v']}),
    ({'v': 'a', 'x': 'v'}, {'x': ['x', 'v', 'a']}),
    ({'v': 'a', 'x': 'v', 'f': 'dfdt'}, {'x': ['x', 'v', 'a'], 'f': ['f', 'dfdt']}),
    ({'v': 'a', 'x': 'v', 'y': 'v', 'h': 'y'}, {'x': ['x', 'v', 'a'], 'h': ['h', 'y', 'v', 'a']}),
    ({'x': 'v', 'v': 'x'}, {}),
])
def test_TimeVarManager_get_tree(ders, expected):
    tree = TimeVarManager.get_tree(ders)
    assert tree == expected


@pytest.mark.parametrize("system, expected", [
    (PointMass('point'), dict(transients=["[x, v]"])),
    (PointMassWithPorts('point'), dict(transients=["[position.x, kinematics.v]"])),
])
def test_TimeVarManager__init__(system, expected):
    m = TimeVarManager(system)
    assert m.context is system
    assert isinstance(m.problem, MathematicalProblem)
    assert m.problem.context is system
    assert set(m.transients.keys()) == set(expected.get("transients", []))
    assert set(m.rates.keys()) == set(expected.get("rates", []))


def test_TimeVarManager_context():
    a = PointMass("A")
    b = PointMass("B")
    m = TimeVarManager(a)
    assert m.context is a
    m.context = b
    assert m.context is b
    m.context = a
    assert m.context is a

    for value in [1, "A"]:
        with pytest.raises(TypeError):
            m.context = value


def test_TimeVarManager_max_time_step(clock):
    class DynamicSystem(System):
        def setup(self):
            self.add_inward('a', np.ones(3))
            self.add_inward('slope', 1.5)
            self.add_inward('omega', np.pi)

            self.add_transient('v', der='a')
            self.add_transient('x', der='v', max_time_step='0.2 * norm(v) / norm(a)')
            self.add_transient('h', der='slope', max_time_step='cos(omega * t)')

    system = DynamicSystem('system')
    m = TimeVarManager(system)

    clock.reset()
    system.a = np.ones(3)
    system.v = np.ones(3)
    assert m.max_time_step() == pytest.approx(0.2)  # limited by transient 'x'
    system.a = np.ones(3)
    system.v = np.zeros(3)
    with pytest.raises(RuntimeError,
        match=r"The maximum time step of \[x, v\] was evaluated to non-positive value 0"
    ):
        m.max_time_step()

    system.a = np.r_[0, 0, 1]
    system.v = np.r_[100, 0, 0]
    assert m.max_time_step() == pytest.approx(1)  # limited by transient 'h'

    clock.time = 1.2
    with pytest.raises(RuntimeError,
        match=r"The maximum time step of h was evaluated to non-positive value -0..."
    ):
        m.max_time_step()
