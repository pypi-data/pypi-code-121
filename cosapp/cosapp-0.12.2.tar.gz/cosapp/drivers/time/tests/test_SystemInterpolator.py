import pytest
import numpy as np

from .conftest import (
    PointMass, PointMassSolution,
    DampedMassSpring, HarmonicOscillatorSolution,
    ScalarOde,
)
from cosapp.drivers import RungeKutta
from cosapp.drivers.time.utils import SystemInterpolator


def test_SystemInterpolator_massSpring():
    t0, t1 = 0, 10
    spring = DampedMassSpring('spring')
    driver = spring.add_driver(RungeKutta(time_interval=(t0, t1)))

    x0, v0 = 0.25, 0.3
    exact = HarmonicOscillatorSolution(spring, x0, v0)

    view = SystemInterpolator(driver)
    view.interp = {
        'x': exact.get_function('x'),
        'v': exact.get_function('v'),
    }
    time = np.linspace(t0, t1, 11)
    for t in time:
        view.exec(t)
        assert spring.x == exact.x(t)
        assert spring.v == exact.v(t)
        assert spring.a == exact.a(t)


def test_SystemInterpolator_pointMass():
    t0, t1 = 0, 10
    p = PointMass('p')
    driver = p.add_driver(RungeKutta(time_interval=(t0, t1)))

    x0 = [-1., 0., 10]
    v0 = [8, 0, 9.5]
    exact = PointMassSolution(p, v0, x0)

    view = SystemInterpolator(driver)
    view.interp = {
        'x': exact.get_function('x'),
        'v': exact.get_function('v'),
    }
    time = np.linspace(t0, t1, 11)
    for t in time:
        view.exec(t)
        assert p.x == pytest.approx(exact.x(t), abs=0)
        assert p.v == pytest.approx(exact.v(t), abs=0)
        assert p.a == pytest.approx(exact.a(t), abs=0)


def test_SystemInterpolator_ode_scenario():
    """Test """
    t0, t1 = 0, 1
    ode = ScalarOde('ode')
    driver = ode.add_driver(RungeKutta(time_interval=(t0, t1)))
    driver.set_scenario(
        values = {
            'df': '0.1 * exp(-t / 5)',
        }
    )
    view = SystemInterpolator(driver)
    view.interp = {
        'f': lambda t: t,  # not the actual solution
    }
    time = np.linspace(t0, t1, 11)
    for t in time:
        view.exec(t)
        assert ode.df == 0.1 * np.exp(-t / 5)
        assert ode.f == t
