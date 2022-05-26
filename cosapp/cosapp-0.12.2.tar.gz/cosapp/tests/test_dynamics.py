"""Integration tests for time drivers
"""
import pytest
import numpy as np

from cosapp.base import System
from cosapp.tests.library.systems import BouncingBall
from cosapp.drivers import NonLinearSolver, RunSingleCase, RungeKutta
from cosapp.recorders import DataFrameRecorder
from typing import Tuple


@pytest.fixture
def ball() -> BouncingBall:
    ball = BouncingBall('ball', g=[0, -9.81])
    ball.mass = 1.5
    ball.cf = 0.2
    ball.cr = 0.98
    return ball


BallCase = Tuple[BouncingBall, RungeKutta]

@pytest.fixture
def ball_case(ball: BouncingBall) -> BallCase:
    """Bouncing ball test case.
    Returns tuple (system, time_driver).
    """
    driver = ball.add_driver(RungeKutta(order=3, dt=0.01))
    driver.time_interval = (0, 20)

    # Add a recorder to capture time evolution in a dataframe
    driver.add_recorder(
        DataFrameRecorder(
            includes = ['x', 'v', 'a', 'n_r*', 'norm(v)'],
        ),
        period = 0.05,
    )
    # Define a simulation scenario
    driver.set_scenario(
        init = {
            'x': np.array([0, 0]),
            'v': np.array([8, 9.5]),
        },
        stop = ball.rebound.filter("norm(v) < 1"),
        # stop = ball.rebound.filter("n_rebounds == 3"),
    )
    return ball, driver


def test_BouncingBall_traj(ball_case: BallCase):
    ball, driver = ball_case
    driver.scenario.stop.trigger = ball.rebound

    ball.run_drivers()

    assert ball.x == pytest.approx([6.416270, 0])
    # Retrieve recorded data
    # data = driver.recorder.export_data()
    # data = data.drop(['Section', 'Status', 'Error code'], axis=1)
    # print("", data, sep="\n")
    # time = np.asarray(data['time'])
    # traj = np.asarray(data['x'].tolist())


def test_BouncingBall_design_cf():
    """Test involving a time driver nested in a nonlinear solver,
    with a system containing a primary event. If events are not
    properly reset at the beginning of each time simulation, the solver
    fails at the first iteration, as the internal state of the event
    is inconsistent.
    Related to https://gitlab.com/cosapp/cosapp/-/issues/90
    """
    class BallDesignCase(System):
        def setup(self):
            ball = self.add_child(BouncingBall('ball', g=[0, -9.81]))
            self.add_event('first_rebound', trigger=ball.rebound.filter('n_rebounds == 0'))
            self.add_event('reach_top', trigger='ball.v[-1] == 0')
            self.add_outward_modevar('t_rebound', init=0.0)
    
        def transition(self) -> None:
            if self.first_rebound.present:
                self.t_rebound = self.time

    s = BallDesignCase('s')
    ball = s.ball
    ball.mass = 1.0
    ball.cf = 0.1
    ball.cr = 1.0

    solver = s.add_driver(NonLinearSolver('solver', tol=1e-9))
    solver.add_driver(RunSingleCase('runner'))
    driver = solver.runner.add_driver(
        RungeKutta(dt=0.05, time_interval=[0, 2], order=2)
    )
    driver.set_scenario(
        init = {
            'ball.x': np.array([0, 0]),
            'ball.v': np.array([8, 9.5]),
        },
        stop = ball.rebound.filter("norm(v) < 0.1"),
    )

    # Setup design problem
    solver.add_unknown('ball.cf', max_rel_step=0.5).add_equation('t_rebound == 1.522')

    # Add recorders, for debug
    # solver.runner.add_recorder(
    #     DataFrameRecorder(includes=['ball.cf', 't_rebound'], hold=True)
    # )
    # driver.add_recorder(
    #     DataFrameRecorder(
    #         includes=[f"ball.{var}" for var in 'x'],
    #         hold=False,
    #     ),
    #     period=0.05,
    # )

    s.ball.cf = 0.5  # first guess
    s.run_drivers()

    # Retrieve recorded data
    # if solver.runner.recorder and driver.recorder:
    #     res = solver.runner.recorder.export_data()
    #     data = driver.recorder.export_data()
    #     data = data.drop(['Section', 'Status', 'Error code'], axis=1)
    #     print("", res, data, sep="\n")

    assert s.ball.cf == pytest.approx(0.1045, rel=1e-3)
