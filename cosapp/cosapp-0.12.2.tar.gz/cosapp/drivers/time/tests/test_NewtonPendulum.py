import pytest
import numpy as np
from cosapp import drivers

from cosapp.systems import System
from cosapp.drivers import RungeKutta
from cosapp.recorders import DataFrameRecorder


class Pendulum(System):
    def setup(self):
        self.add_inward('L', 1.00, desc='Length of the rod')
        self.add_inward('g', 9.81, desc='Gravitational acceleration')
        self.add_outward('acc', 1., desc="Angular acceleration of the mass")
        
        self.add_transient('omega', der='acc', desc="Angular velocity")
        self.add_transient('theta', der='omega', desc="Positional angle")

    def compute(self):
        self.acc = -(self.g / self.L) * np.sin(self.theta)


class NewtonPendulum(System):
    def setup(self):
        self.add_child(Pendulum('p1'), pulling=['L', 'g'])
        self.add_child(Pendulum('p2'), pulling=['L', 'g'])
        
        contact = self.add_event('contact', trigger="p1.theta == p2.theta")
        self.add_event('collision', trigger=contact.filter("p1.omega > p2.omega"))

    def transition(self):
        if self.collision.present:
            self.p1.omega, self.p2.omega = self.p2.omega, self.p1.omega


def test_NewtonPendulum():
    pend = NewtonPendulum("pend")

    driver = pend.add_driver(
        RungeKutta(order=3, dt=0.01, time_interval=[0, 2])
    )
    driver.set_scenario(
        init = {
            "p1.theta" : np.radians(-60),
            "p1.omega" : 2,
            "p2.theta" : np.radians(22),
            "p2.omega" : 0.5,
        },
        values = {
            "L" : 0.5,
            "g" : 9.81,
        },
    )
    driver.add_recorder(
        DataFrameRecorder(includes=['p?.theta', 'p?.omega']),
        period = 0.05,
    )

    # Run simulation
    pend.run_drivers()

    data = driver.recorder.export_data()
    theta1 = np.asarray(data['p1.theta'])
    theta2 = np.asarray(data['p2.theta'])
    # Check that theta1 <= theta2 within numerical tolerance:
    assert all(theta1 - theta2 < 1e-15)
    # Check recorded events
    recorded_events = driver.recorded_events
    assert len(recorded_events) == 3
    assert [record.time for record in recorded_events] == pytest.approx(
        [0.31293088163661, 1.0724999600884, 1.831490584856]
    )
    for record in recorded_events:
        assert len(record.events) == 2
        assert record.events[0] is pend.contact  # first in record is primary event
        assert set(record.events) == {pend.contact, pend.collision}


def test_NewtonPendulum_limit():
    """Limit case where the two masses move jointly (constant contact)."""
    pend = NewtonPendulum("pend")

    driver = pend.add_driver(
        RungeKutta(order=3, dt=0.01, time_interval=[0, 1])
    )
    driver.set_scenario(
        init = {
            "p1.theta" : np.radians(10),
            "p1.omega" : -2,
            "p2.theta" : np.radians(10),
            "p2.omega" : -2,
        },
        values = {
            "L" : 0.5,
            "g" : 9.81,
        },
    )
    driver.add_recorder(
        DataFrameRecorder(includes=['p?.theta', 'p?.omega']),
        period = 0.05,
    )

    # Run simulation
    pend.run_drivers()

    # Check that no event was recorded
    assert len(driver.event_data) == 0
    assert len(driver.recorded_events) == 0

    data = driver.recorder.export_data()
    # print(data.drop(['Section', 'Status', 'Error code'], axis=1))
    theta1 = np.asarray(data['p1.theta'])
    theta2 = np.asarray(data['p2.theta'])
    # Check that theta1 == theta2:
    assert theta1 == pytest.approx(theta2, abs=1e-15)


def test_NewtonPendulum_stop():
    """Same as base test, with a stop criterion based on a filtered event."""
    pend = NewtonPendulum("pend")

    driver = pend.add_driver(
        RungeKutta(order=3, dt=0.01, time_interval=[0, 2])
    )
    driver.set_scenario(
        init = {
            "p1.theta" : np.radians(-60),
            "p1.omega" : 2,
            "p2.theta" : np.radians(22),
            "p2.omega" : 0.5,
        },
        values = {
            "L" : 0.5,
            "g" : 9.81,
        },
        stop = pend.contact.filter('p1.theta < 0'),
    )
    driver.add_recorder(
        DataFrameRecorder(includes=['p?.theta', 'p?.omega']),
        period = 0.05,
    )

    # Run simulation
    pend.run_drivers()

    data = driver.recorder.export_data()
    theta1 = np.asarray(data['p1.theta'])
    theta2 = np.asarray(data['p2.theta'])
    # Check that theta1 <= theta2 within numerical tolerance:
    assert all(theta1 - theta2 < 1e-15)
    assert pend.p1.theta == pytest.approx(pend.p2.theta, abs=1e-15)
    assert pend.p1.theta == pytest.approx(-0.1186766797)
    # Check recorded events
    recorded_events = driver.recorded_events
    assert len(recorded_events) == 2

    # First event record
    record = recorded_events[0]
    assert record.time == pytest.approx(0.31293088163661)
    assert len(record.events) == 2
    assert record.events[0] is pend.contact  # first in record is primary event
    assert set(record.events) == {pend.contact, pend.collision}

    # Second event record
    record = recorded_events[1]
    assert record.time == pytest.approx(1.0724999600884)
    assert len(record.events) == 3
    assert record.events[0] is pend.contact  # first in record is primary event
    assert set(record.events) == {pend.contact, pend.collision, driver.scenario.stop}
