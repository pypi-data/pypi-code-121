import pytest

import numpy as np
from cosapp.drivers.time.utils import TimeUnknownStack, TimeVarManager
from cosapp.systems import System
from .conftest import PointMass, PointMassWithPorts, DevilCase


@pytest.fixture(scope="function")
def make_case():
    def factory(cls, name, **options):
        system = cls(name, **options)
        manager = TimeVarManager(system)
        return system, manager
    return factory


@pytest.mark.parametrize("cls, branch, name", [
    (PointMass, ['x', 'v', 'a'], "[x, v]"),
    (PointMassWithPorts, ['position.x', 'kinematics.v', 'a'], "[position.x, kinematics.v]"),
])
def test_TimeUnknownStack__init__(make_case, cls, branch, name):
    point, manager = make_case(cls, "point")
    assert set(manager.transients.keys()) == {name}
    stack = manager.transients[name]
    assert isinstance(stack, TimeUnknownStack)
    assert stack.name == name


def test_TimeUnknownStack_der_1(make_case):
    point, manager = make_case(PointMass, "point")
    stack = manager.transients["[x, v]"]
    assert np.array_equal(stack.value, np.zeros(6))

    point.x = np.zeros_like(point.x)
    point.v = np.full_like(point.v, 0.1)
    point.k = 0.0
    point.run_once()
    # stack.value is not changed by x or v, because the object holds
    # a copy of [x, v], evaluated at construction. Should this be changed?
    assert np.array_equal(stack.value, np.zeros(6))
    # time derivative and max dt are dynamically evaluated
    assert np.array_equal(stack.d_dt, [0.1, 0.1, 0.1, 0, 0, -9.81])
    assert stack.max_time_step == pytest.approx(0.981)

    point.k = 0.1
    point.mass = 1.0
    point.run_once()
    assert np.array_equal(stack.value, np.zeros(6))
    assert np.allclose(point.a, [-0.01, -0.01, -9.82], rtol=1e-12)
    assert np.allclose(stack.d_dt, [0.1, 0.1, 0.1, -0.01, -0.01, -9.82], rtol=1e-12)
    assert stack.max_time_step == pytest.approx(0.1 * np.linalg.norm(point.a))


def test_TimeUnknownStack_der_2(make_case):
    point, manager = make_case(PointMassWithPorts, "point")
    stack = manager.transients["[position.x, kinematics.v]"]
    assert np.array_equal(stack.value, np.zeros(6))

    point.position.x = np.zeros_like(point.position.x)
    point.kinematics.v = np.full_like(point.kinematics.v, 0.1)
    point.k = 0.0
    point.run_once()
    # stack.value is not changed by x or v, because the object holds
    # a copy of [x, v], evaluated at construction. Should this be changed?
    assert np.array_equal(stack.value, np.zeros(6))
    # time derivative and max dt are dynamically evaluated
    assert np.array_equal(stack.d_dt, [0.1, 0.1, 0.1, 0, 0, -9.81])
    assert stack.max_time_step == pytest.approx(0.981)

    point.k = 0.1
    point.mass = 1.0
    point.run_once()
    a = point.a
    assert np.array_equal(stack.value, np.zeros(6))
    assert np.allclose(a, [-0.01, -0.01, -9.82], rtol=1e-12)
    assert np.allclose(stack.d_dt, [0.1, 0.1, 0.1, -0.01, -0.01, -9.82], rtol=1e-12)
    assert stack.max_time_step == pytest.approx(0.1 * np.linalg.norm(a))

@pytest.mark.parametrize("pulling", [
    None, ["x"], ["x", "v"], ["v", "a"], ["a"], ["alpha"], ["omega", "zeta"], ["zeta"]
])
def test_TimeUnknownStack_multisystems(pulling):
    devil = DevilCase("devil")
    top = System("top")
    top.add_child(devil, pulling=pulling)
    manager = TimeVarManager(top)
    assert len(manager.transients) == 4
    stack_vector = manager.transients[f"{devil.name}[x, v]"]
    assert np.array_equal(stack_vector.value, np.zeros(6))

    stack_scalar = manager.transients[f"{devil.name}[alpha, omega]"]
    assert np.array_equal(stack_scalar.value, np.zeros(2))

    new_vector =  np.random.randn(6)
    stack_vector.value = new_vector
    new_scalar = np.random.randn(2)
    stack_scalar.value = new_scalar
    top.run_once()  # Propagate the unknown if a pulling occurred
    assert devil.x == pytest.approx(new_vector[:3])
    assert devil.v == pytest.approx(new_vector[3:])
    assert devil.alpha == pytest.approx(new_scalar[0])
    assert devil.omega == pytest.approx(new_scalar[1])


def test_TimeUnknownStack_value(make_case):
    point, manager = make_case(PointMass, "point")
    stack = manager.transients["[x, v]"]
    # Test value getter
    assert np.array_equal(stack.value[:3], point.x)
    assert np.array_equal(stack.value[3:], point.v)
    # Test value setter
    stack.value = np.array(range(6), dtype=float)
    assert np.array_equal(point.x, [0, 1, 2])
    assert np.array_equal(point.v, [3, 4, 5])
