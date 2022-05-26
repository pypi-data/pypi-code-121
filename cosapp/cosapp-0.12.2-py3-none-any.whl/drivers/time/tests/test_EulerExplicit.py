import pytest
import logging

import numpy as np
from cosapp.drivers import EulerExplicit, NonLinearSolver
import cosapp.recorders as recorders


def test_EulerExplicit_init_default():
    driver = EulerExplicit()
    assert driver.owner is None
    assert driver.dt is None
    assert driver.time_interval is None
    assert driver.name == "Euler"


def test_EulerExplicit_ode_solve_1(ode_case_1):
    # First run
    ode, driver = ode_case_1(EulerExplicit, dt=1e-3, time_interval=[0, 1])

    ode.run_drivers()
    start, end = driver.time_interval
    assert ode.f == pytest.approx(ode(end), 1e-3)
    assert end == 1

    # Second run, where end time is not a multiple of time step
    ode, driver = ode_case_1(EulerExplicit, dt=1e-3, time_interval=[0, 1 + 2e-4])
    ode.run_drivers()
    start, end = driver.time_interval
    assert ode.f == pytest.approx(ode(end), 1e-3)
    assert end == pytest.approx(1.0002)


def test_EulerExplicit_stop(scalar_ode_case, caplog):
    """Test scenario with stop criterion."""
    ode, driver = scalar_ode_case(EulerExplicit, dt=0.1, time_interval=[0, 1])

    driver.set_scenario(
        init = {'f': 0},
        values = {'df': 0.5},
        stop = f"f**2 > {0.123**2}",
    )
    driver.add_recorder(
        recorders.DataFrameRecorder(includes=['f']),
        period = 0.1,
    )

    with caplog.at_level(logging.INFO):
        ode.run_drivers()
    data = driver.recorder.export_data()
    assert ode.f == pytest.approx(0.123, rel=1e-14)
    assert ode.t == pytest.approx(0.246, rel=1e-14)
    assert np.asarray(data['time']) == pytest.approx([0, 0.1, 0.2, 0.246, 0.246], abs=1e-14)
    assert len(caplog.records) > 1
    assert any(
        "Stop criterion met at t =" in record.message
        for record in caplog.records
    )



@pytest.mark.parametrize("dt", [
    0.1, 0.01,
    # 1e-3,  # long
])
def test_EulerExplicit_twoTanks(two_tank_case, two_tank_solution, dt):
    system, driver = two_tank_case(EulerExplicit, dt=dt, time_interval=[0, 5])
    solver = driver.add_child(NonLinearSolver('solver', factor=1.0))

    h1_0, h2_0 = init = (3, 1)

    driver.set_scenario(
        name = 'run',
        init = {
            'tank1.height': h1_0,  # initial conditions
            'tank2.height': h2_0,
        },
        values = {
            'pipe.D': 0.07,  # fixed values
            'pipe.L': 2.5,
            'tank1.area': 2,
        }
    )
    
    assert driver.scenario.context is system
    assert driver.scenario.name == 'run'
    
    driver.add_recorder(recorders.DataFrameRecorder(includes='tank?.height'), period=0.1)
    # driver.add_recorder(recorders.DSVRecorder('twoTanks_Euler.csv', includes=['tank?.height', ]), period=0.1)
    assert driver.recording_period == 0.1

    system.run_drivers()

    assert system.tank1.height < 3
    assert system.tank2.height > 1
    assert system.tank1.height == pytest.approx(system.tank2.height, rel=1e-3)

    df = driver.recorder.export_data()
    assert len(df) == 51
    solution = two_tank_solution(system, init)
    assert solution.characteristic_time == pytest.approx(0.5766040318109212)
    time = np.asarray(df['time'])
    error = 0
    for t, h1 in zip(time, df['tank1.height']):
        exact = solution(t)
        error = max(error, abs(h1 - exact[0]))
    # Test that maximum error ~ dt
    assert error < 0.3 * dt
    assert error > 0.2 * dt


def test_EulerExplicit_multimode_scalar_ode(multimode_scalar_ode_case):
    system, driver = multimode_scalar_ode_case(
        EulerExplicit, time_interval=(0, 1), dt=0.1,
    )
    driver.add_recorder(recorders.DataFrameRecorder(includes=['f', 'df']), period=0.1)

    system.snap.trigger = "f > 0.347"

    driver.set_scenario(
        init = {'f': 0},
        values = {'df': '0 if snapped else 1'},
    )
    system.run_drivers()

    data = driver.recorder.export_data()
    # print(data)
    assert system.f == pytest.approx(0.347, rel=1e-12)
    assert system.df == 0
    assert np.asarray(data['time']) == pytest.approx(
        [0, 0.1, 0.2, 0.3, 0.347, 0.347, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
        abs=1e-14,
    )
    assert np.asarray(data['df']) == pytest.approx(
        [1] * 5 + [0] * 8, abs=1e-14,
    )
