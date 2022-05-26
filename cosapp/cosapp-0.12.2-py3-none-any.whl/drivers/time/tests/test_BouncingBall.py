import pytest
import numpy as np

from cosapp.systems import System
from cosapp.recorders import DataFrameRecorder
from cosapp.drivers import RungeKutta


class PointDynamics(System):
    """Point mass dynamics"""
    def setup(self):
        self.add_inward("mass", 1.0)
        self.add_inward("acc_ext", np.zeros(3))
        self.add_inward("force_ext", np.zeros(3))

        self.add_outward("force", np.zeros(3))
        self.add_outward("acc", np.zeros(3))

    def compute(self):
        self.force = self.force_ext + self.mass * self.acc_ext
        self.acc = self.force / self.mass


class PointFriction(System):
    """Point mass ~ v**2 friction model"""
    def setup(self):
        self.add_inward('v', np.zeros(3), desc="Velocity")
        self.add_inward('cf', 0.1, desc="Friction coefficient")

        self.add_outward("force", np.zeros(3))

    def compute(self):
        self.force = (-self.cf * np.linalg.norm(self.v)) * self.v


class PointMass(System):
    def setup(self):
        self.add_child(PointFriction('friction'), pulling=['cf', 'v'])
        self.add_child(PointDynamics('dynamics'), pulling={
            'mass': 'mass',
            'force': 'force',
            'acc_ext': 'g',
            'acc': 'a',
        })

        self.connect(self.friction, self.dynamics, {"force": "force_ext"})

        self.add_transient('v', der='a')
        self.add_transient('x', der='v')

        self.g = np.r_[0, 0, -9.81]
        self.exec_order = ['friction', 'dynamics']


class BouncingBall(System):
    def setup(self):
        self.add_child(PointMass('point'), pulling=[
            'mass', 'x', 'v', 'a', 'cf', 'g',
        ])
        self.add_event('rebound', trigger="x[2] <= 0")

    def transition(self):
        if self.rebound.present:
            v = self.v
            if abs(v[2]) < 1e-6:
                v[2] = 0
            else:
                v[2] *= -1


@pytest.fixture
def ball():
    return BouncingBall('ball')


@pytest.fixture
def ball_case(ball):
    """Bouncing ball + driver test case"""
    driver = ball.add_driver(RungeKutta(order=3))
    driver.time_interval = (0, 4)
    driver.dt = 0.01

    # Add a recorder to capture time evolution in a dataframe
    driver.add_recorder(DataFrameRecorder(includes=['x', 'v', 'a']), period=0.05)

    # Initial conditions
    x0 = [0, 0, 0]
    v0 = [8, 0, 9.5]

    # Define a simulation scenario
    driver.set_scenario(
        init = {'x': np.array(x0), 'v': np.array(v0)},
        values = {'mass': 1.5, 'cf': 0.2},
    )

    return ball, driver


def test_BouncingBall(ball_case):
    ball, driver = ball_case

    ball.run_drivers()

    # Retrieve recorded data
    data = driver.recorder.export_data()
    x = np.asarray(data['x'].tolist())
    # Check that all positions are above ground level,
    # within numerical tolerance
    assert min(x[:, 2]) > -1e-13
    assert len(driver.recorded_events) == 3
    assert [record.time for record in driver.recorded_events] == pytest.approx(
        [1.457205, 2.536008, 3.441106]
    )


def test_BouncingBall_final(ball_case):
    """Bouncing ball case with final rebound event.
    """
    ball, driver = ball_case
    ball.rebound.final = True

    ball.run_drivers()

    # Retrieve recorded data
    data = driver.recorder.export_data()
    x = np.asarray(data['x'].tolist())
    assert min(x[:, 2]) > -1e-13
    assert ball.x[2] == pytest.approx(0)
    assert len(driver.recorded_events) == 1
    assert driver.recorded_events[0].time == pytest.approx(1.457205)


def test_BouncingBall_stop(ball):
    """Bouncing ball case with stop criterion based on rebound event.
    """
    driver = ball.add_driver(RungeKutta(order=3))
    driver.time_interval = (0, 4)
    driver.dt = 0.01

    # Add a recorder to capture time evolution in a dataframe
    driver.add_recorder(DataFrameRecorder(includes=['x', 'v', 'a']), period=0.05)

    # Initial conditions
    x0 = [0, 0, 0]
    v0 = [8, 0, 9.5]

    # Define a simulation scenario
    driver.set_scenario(
        init = {'x': np.array(x0), 'v': np.array(v0)},
        values = {'mass': 1.5, 'cf': 0.2},
        stop = ball.rebound,
    )

    ball.run_drivers()

    # Retrieve recorded data
    data = driver.recorder.export_data()
    x = np.asarray(data['x'].tolist())
    assert min(x[:, 2]) > -1e-13
    assert len(driver.recorded_events) == 1
    record = driver.recorded_events[-1]
    assert len(record.events) == 2
    assert record.time == pytest.approx(1.457205)
    assert record.events[0] is ball.rebound
    assert record.events[1] is driver.scenario.stop
