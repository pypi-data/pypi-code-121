import pytest

import numpy as np
from cosapp.systems import System
from cosapp.drivers import NonLinearSolver, RunSingleCase, RungeKutta
from cosapp.drivers.time.scenario import Interpolator
from cosapp.recorders import DataFrameRecorder
from .conftest import case_factory, PointMass, PointMassWithPorts


def rel_error(actual, expected):
    res = lambda a, b: abs(a) if b == 0 else abs(a / b - 1)
    if isinstance(expected, np.ndarray):
        return np.array([res(a, b) for a, b in zip(actual, expected)])
    else:
        return res(actual, expected)


def test_RungeKutta_init_default():
    driver = RungeKutta()
    assert driver.owner is None
    assert driver.dt is None
    assert driver.time_interval is None
    assert driver.order > 1
    assert driver.name == "RK"


@pytest.mark.parametrize("settings, expected", [
    (dict(), dict()),
    (dict(order=3), dict(order=3)),
    (dict(order=4), dict(order=4)),
    (dict(dt=0.1), dict(dt=0.1)),
    (dict(dt=0.1, time_interval=(0, 1)), dict(dt=0.1, time_interval=(0, 1))),
    (dict(dt=0.1, time_interval=(0, 1), order=3), dict(dt=0.1, time_interval=(0, 1), order=3)),
    (dict(order=0), dict(error=ValueError)),
    (dict(order=1), dict(error=ValueError)),
    (dict(order=5), dict(error=ValueError)),
])
def test_RungeKutta_init_args(settings, expected):
    error = expected.get('error', None)
    if error is None:
        driver = RungeKutta(**settings)
        assert driver.dt == expected.get('dt', None)
        assert driver.time_interval == expected.get('time_interval', None)
        assert driver.order == expected.get('order', 2)
        assert len(driver._RungeKutta__coefs) == driver.order
    else:
        with pytest.raises(error):
            RungeKutta(**settings)


@pytest.mark.parametrize("order, expected", [
    (2, dict(value=2)),
    (3, dict(value=3)),
    (4, dict(value=4)),
    (0, dict(error=ValueError, match="order.*invalid value")),
    (1, dict(error=ValueError, match="order.*invalid value")),
    (5, dict(error=ValueError, match="order.*invalid value")),
    (0.5, dict(error=TypeError, match="order.*should be int")),
    ("0.5", dict(error=TypeError, match="order.*should be int")),
])
def test_RungeKutta_order(order, expected):
    driver = RungeKutta()
    assert driver.dt is None
    assert driver.time_interval is None
    assert driver.order > 1
    assert len(driver._RungeKutta__coefs) == driver.order

    error = expected.get('error', None)
    if error is None:
        driver.order = order
        assert driver.order == expected['value']
        assert len(driver._RungeKutta__coefs) == driver.order
    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            driver.order = order


@pytest.mark.parametrize("settings, tol", [
    (dict(dt=1e-2, order=2, time_interval=[0, 1]), 1e-4),
    (dict(dt=1e-2, order=3, time_interval=[0, 1]), 1e-7),
    (dict(dt=1e-2, order=3, time_interval=[0, 1.007]), 1e-7),  # end time is not a multiple of time step
    (dict(dt=1e-2, order=4, time_interval=[0, 1.007]), 1e-10),
    (dict(dt=1e-3, time_interval=[0, 1]), 1e-7),
    (dict(dt=1e-3, time_interval=[0, 1.0003]), 1e-7),
])
def test_RungeKutta_ode_solve_1(ode_case_1, settings, tol):
    # First run
    ode, driver = ode_case_1(RungeKutta, **settings)
    driver.set_scenario(init={"f": 0})
    ode.run_drivers()
    end_time = driver.time_interval[1]
    assert ode.time == end_time
    assert ode.f == pytest.approx(ode(end_time), rel=tol)


@pytest.mark.parametrize("dt", [
    0.1,
    0.01,
    # 0.001,  # passed, but long
])
def test_RungeKutta_twoTanks(two_tank_case, two_tank_solution, dt):
    system, driver = two_tank_case(RungeKutta, dt=dt, time_interval=[0, 5], order=2)
    solver = driver.add_child(NonLinearSolver('solver', factor=1.0))
    
    # mu_0, mu_inf = 1e-2, 3e-3
    h1_0, h2_0 = init = (3, 1)

    driver.set_scenario(
        init = {
            'tank1.height': h1_0,  # initial conditions
            'tank2.height': h2_0,
        },
        values = {
            'pipe.D': 0.07,  # fixed values
            'pipe.L': 2.5,
            'tank1.area': 2,
            # 'pipe.mu': f'{mu_0} + ({mu_inf} - {mu_0}) * (1 - exp(-t / 5))'  # explicit time dependency
        }
    )
    
    driver.add_recorder(DataFrameRecorder(includes='tank?.height'), period=0.1)
    assert driver.recording_period == 0.1

    system.run_drivers()

    assert system.tank1.height < 3
    assert system.tank2.height > 1
    assert system.tank1.height == pytest.approx(system.tank2.height, rel=1e-3)

    data = driver.recorder.export_data()
    assert len(data) == 51
    solution = two_tank_solution(system, init)
    assert solution.characteristic_time == pytest.approx(0.5766040318109212)
    assert driver.dt < solution.characteristic_time
    time = np.asarray(data['time'])
    error = 0
    for t, h1 in zip(time, data['tank1.height']):
        exact = solution(t)
        error = max(error, abs(h1 - exact[0]))
    # Test that maximum error ~ dt^2
    assert error < 0.2 * dt**2
    assert error > 0.1 * dt**2


@pytest.mark.parametrize("case", [
    dict(
        function="cos(2.5 * t)", init=0, interval=[0, 5],
        solution=lambda t: np.sin(2.5 * t) / 2.5,
    ),
    dict(
        init=1, interval=[0, 5],
        function="exp({a} * t) * ({a} * cos({w} * t) - {w} * sin({w} * t))".format(a=-0.55, w=1.84),
        solution=lambda t: np.exp(-0.55 * t) * np.cos(1.84 * t),
    ),
    # Case with boundary condition from tabulated data
    dict(
        function=Interpolator([[0, 0], [1, 1], [10, -17]]),  # F(t) = t if t < 1 else 3 - 2 * t
        init=0, interval=[0, 2],
        solution=lambda t: 0.5 * t**2 if t < 1 else 1.5 + 3 * (t - 1) - t**2,
    ),
])
@pytest.mark.parametrize("settings, tol", [
    (dict(order=2, dt=1e-2), 1e-3),
    (dict(order=4, dt=1e-2), 1e-7),
])
def test_RungeKutta_scalar_ode(scalar_ode_case, case, settings, tol):
    """Integration of simple scalar ODEs of the kind df/dt = F(t)"""
    settings['time_interval'] = case.get('time_interval', [0, 5])
    ode, driver = scalar_ode_case(RungeKutta, **settings)
    driver.add_recorder(DataFrameRecorder(includes='f'), period=0.01)

    driver.set_scenario(
        init = {'f': case['init']},
        values = {'df': case['function']},
    )
    ode.run_drivers()
    # Retrieve recorded data and check accuracy
    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    result = np.asarray(data['f'], dtype=float)
    solution = case['solution']
    error = np.array([rel_error(num, solution(t)) for (t, num) in zip(time, result)])
    assert error.max() < tol


@pytest.mark.parametrize("settings, expected", [
    (dict(order=2, dt=0.5), dict(tol=5e-2, dt_min=pytest.approx(0.05738592))),
    (dict(order=4, dt=0.5), dict(tol=1e-4, dt_min=pytest.approx(0.08038455))),
    (dict(order=4, dt=0.2), dict(tol=1e-4, dt_min=pytest.approx(0.028292196))),
    (dict(order=2, dt=0.1), dict(tol=1e-3, dt_min=pytest.approx(0.1))),
])
def test_RungeKutta_scalar_ode_limited_dt(settings: dict, expected: dict):
    class ExpOde(System):
        """System representing exponential function from ODE dy/dt = a * y"""
        def setup(self):
            self.add_inward('a', 1.0)
            self.add_inward('y', 1.0)
            self.add_transient('y', der='a * y', max_abs_step=1)
            # Define z, similar to y, with an equivalent (yet different) time step limiter
            self.add_inward('z', 1.0)
            self.add_transient('z', der='a * z', max_time_step='1 / abs(a * z)')

    settings.setdefault('time_interval', [0, 8])
    settings['record_dt'] = True
    ode = ExpOde('ode')
    driver = ode.add_driver(RungeKutta(**settings))
    driver.add_recorder(DataFrameRecorder(includes=['y', 'z']), period=None)

    driver.set_scenario(
        init = {'y': 1, 'z': 1},
        values = {'a': 0.4},
    )
    ode.run_drivers()
    # Retrieve recorded data and check accuracy
    data = driver.recorder.export_data()
    times = np.asarray(data['time'])
    ys = np.asarray(data['y'], dtype=float)
    zs = np.asarray(data['z'], dtype=float)
    # Check that y and y values are identical
    assert np.array_equal(ys, zs)
    solution = lambda t: np.exp(ode.a * t)
    error = np.array([rel_error(num, solution(t)) for (t, num) in zip(times, ys)])
    assert error.max() < expected['tol']
    dts = driver.recorded_dt
    assert np.array_equal(dts, sorted(dts, reverse=True))
    assert dts.max() <= driver.dt
    assert dts.min() == expected.get('dt_min')
    assert dts.max() == expected.get('dt_max', driver.dt)


@pytest.mark.parametrize("settings, tol", [
    (dict(order=2, dt=1e-2), 1e-8),
    (dict(order=4, dt=5e-2), 1e-8),
    (dict(order=4, dt=1e-2), 1e-10),
])
def test_RungeKutta_vector_ode(vector_ode_case, settings, tol):
    ode, driver = vector_ode_case(RungeKutta, **settings, time_interval=(0, 5))
    driver.add_recorder(DataFrameRecorder(includes='v'), period=0.1)

    x0 = np.array([0.2, 1.2, -3.14])
    driver.set_scenario(
        init = {'v': np.array(x0)},
        values = {'dv': '[2 * t, 1 / (1 + t), exp(-t)]'}
    )

    ode.run_drivers()
    # Retrieve recorded data and check accuracy
    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    solution = lambda t, x0: np.array([t**2, np.log(1 + t), 1 - np.exp(-t)]) + x0
    result = np.asarray([value for value in data['v']])
    error = np.zeros_like(ode.v)
    for i, t in enumerate(time):
        exact = solution(t, x0)
        error = np.maximum(rel_error(result[i], exact), error)
    assert error.max() < tol


@pytest.mark.parametrize("order, dt, tol", [
    (2, 1e-2, 1e-5),
    (3, 5e-2, 1e-6),
])
def test_RungeKutta_point_mass(point_mass_case, point_mass_solution, order, dt, tol):
    settings = dict(order=order, time_interval=(0, 2), dt=dt)
    system, driver = point_mass_case(RungeKutta, **settings)

    driver.add_recorder(DataFrameRecorder(includes=['x', 'v', 'a']), period=0.1)

    x0 = [-1., 0., 10]
    v0 = [8, 0, 9.5]
    driver.set_scenario(
        init = dict(x = np.array(x0), v = np.array(v0)),
        values = dict(mass = 1.5, k = 0.5),
    )

    system.run_drivers()

    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    solution = point_mass_solution(system, v0, x0)
    error = np.zeros(3)
    for t, x in zip(time, data['x']):
        error = np.maximum(error, rel_error(x, solution.x(t)))
    context = f"dt = {driver.dt}, order = {driver.order}"
    assert error.max() < tol, context


def test_RungeKutta_point_mass_stop(point_mass_case):
    """"Point mass case with stop criterion"""
    settings = dict(order=2, time_interval=(0, 2), dt=0.01)
    system, driver = point_mass_case(RungeKutta, **settings)

    driver.add_recorder(DataFrameRecorder(includes=['x', 'v', 'a']), period=0.1)

    x0 = [-1., 0, 0]
    v0 = [8, 0, 9.5]
    driver.set_scenario(
        init = {'x': np.array(x0), 'v': np.array(v0)},
        stop = f"x[2] == {x0[2]}",
        values = {'mass': 1.5, 'k': 0.5},
    )
    system.run_drivers()

    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    assert system.x[2] == pytest.approx(x0[2])
    assert time[-1] == pytest.approx(1.7647, abs=1e-4)
    assert len(driver.recorded_events) == 1
    record = driver.recorded_events[-1]
    assert record.events[0] is driver.scenario.stop
    assert record.time == time[-1]


@pytest.mark.parametrize("exec_order", [
    ['point', 'bogus'],
    ['bogus', 'point'],
])
@pytest.mark.parametrize("case_settings, expected", [
    (
        dict(time_interval=(0, 2), dt=0.1, order=3, x0=[0, 0, 10], target=[10, 0, 10]),
        dict(v0=pytest.approx([8.5860, 0, 11.726], rel=1e-4))
    ),
    (
        dict(time_interval=(0, 3), dt=0.1, order=3, x0=[0, 0, 0], target=[10, 0, 0], tol=1e-8),
        dict(v0=pytest.approx([7.1882, 0, 18.908], rel=1e-4))
    ),
])
def test_RungeKutta_point_mass_target(exec_order, case_settings: dict, expected: dict):
    """Balistic test: combination of a nonlinear solver and a time driver,
    in order to find the initial velocity condition leading to the trajectory reaching
    a target point after a given amount of time."""

    class Bogus(System):
        def setup(self):
            self.add_inward('x', np.zeros(3))
            self.add_outward('foo', np.zeros(3), desc='Bogus quantity computed from position `x`')
        
        def compute(self):
            self.foo = self.x**2

    class PointMassTarget(System):
        def setup(self):
            self.add_inward('v0', np.zeros(3), desc='Initial velocity')
            self.add_child(PointMass('point'), pulling=['x', 'v'])
            self.add_child(Bogus('bogus'), pulling='x')

            self.exec_order = exec_order

    # Set test case
    settings = case_settings.copy()
    settings.setdefault('order', 2)
    settings.setdefault('time_interval', (0, 2))
    target_point = settings.pop('target')
    xtol = settings.pop('tol', 1e-5)  # tolerance on target point

    x0 = settings.pop('x0', np.zeros(3))  # initial point position

    traj = PointMassTarget('traj')
    assert list(traj.exec_order) == exec_order
    solver = traj.add_driver(NonLinearSolver('solver', factor=0.9, tol=xtol))
    target = solver.add_child(RunSingleCase('target'))
    driver = target.add_child(RungeKutta(**settings))

    target.set_init({'v0': np.array([1, 1, 1])})
    target.add_unknown('v0').add_equation(f"x == {target_point}")

    # Define a simulation scenario
    driver.set_scenario(
        init = {'x': x0, 'v': 'v0'},
        values = {'point.mass': 1.5, 'point.k': 0.9}
    )

    traj.run_drivers()

    # Check that current position is target point
    assert traj.time == pytest.approx(driver.time_interval[1], abs=1e-12)
    assert traj.x == pytest.approx(target_point, abs=xtol)
    # Check that pulling did not shadow subsystem variables
    assert traj.point.x == pytest.approx(traj.x, abs=0)
    assert traj.bogus.x == pytest.approx(traj.x, abs=0)
    # Check initial velocity solution
    assert traj.v0 == expected['v0']


@pytest.mark.parametrize("hold", [True, False])
def test_RungeKutta_point_mass_target_recorder(hold):
    """Same as `test_RungeKutta_point_mass_target`, but
    checking that the inner recorder has the right size
    at the end of the simulation.
    """
    class PointMassTarget(System):
        def setup(self):
            self.add_inward('v0', np.zeros(3), desc='Initial velocity')
            self.add_child(PointMass('point'), pulling=['x', 'v'])

    # Set test case
    x0 = [0, 0, 10]  # initial point position
    target_point = [10, 0, 10]

    traj = PointMassTarget('traj')
    solver = traj.add_driver(NonLinearSolver('solver', tol=1e-9))
    target = solver.add_child(RunSingleCase('target'))
    driver = target.add_child(
        RungeKutta(order=3, time_interval=(0, 2), dt=0.1)
    )

    target.set_init({'v0': [1, 1, 1]})
    target.add_unknown('v0').add_equation(f"x == {target_point}")
    target.add_recorder(DataFrameRecorder(includes=['v0'], hold=True))

    # Define a simulation scenario
    driver.set_scenario(
        init = {'x': x0, 'v': 'v0'},
        values = {'point.mass': 1.5, 'point.k': 0.9}
    )
    driver.add_recorder(
        DataFrameRecorder(includes=['x', 'v', 'a'], hold=hold),
        period=0.1,
    )

    traj.run_drivers()

    assert target.recorder.hold
    assert driver.recorder.hold == hold

    case_data = target.recorder.export_data()
    time_data = driver.recorder.export_data()

    n_iter = len(case_data)
    assert n_iter > 0
    assert n_iter < 10

    if driver.recorder.hold:
        # Time series recorded at each iteration
        assert len(time_data) == 21 * n_iter
    else:
        # Time series recorded at last iteration
        assert len(time_data) == 21

    # Check that current position is target point
    assert traj.x == pytest.approx(target_point, abs=1e-5)
    # Check initial velocity solution
    assert traj.v0 == pytest.approx([8.5860, 0, 11.726], rel=1e-4)


@pytest.mark.parametrize("order, dt, tol", [
    (2, 1e-2, 1e-5),
    (3, 5e-2, 1e-6),
])
def test_RungeKutta_pointMassWithPorts(pointMassWithPorts_case, point_mass_solution, order, dt, tol):
    settings = dict(order=order, time_interval=(0, 2), dt=dt)
    system, driver = pointMassWithPorts_case(RungeKutta, **settings)

    includes = ['pos*.x', 'kin*.v', 'a']
    driver.add_recorder(DataFrameRecorder(includes=includes), period=0.1)

    x0 = [-1., 0., 10]
    v0 = [8, 0, 9.5]
    driver.set_scenario(
        init = {"position.x": np.array(x0), "kinematics.v": np.array(v0)},
        values = {"mass": 1.5, "k": 0.5},
    )

    system.run_drivers()

    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    traj = np.asarray(data['position.x'])
    solution = point_mass_solution(system, v0, x0)
    error = np.zeros(3)
    for t, x in zip(time, traj):
        error = np.maximum(error, rel_error(x, solution.x(t)))
    context = f"dt = {driver.dt}, order = {driver.order}"
    assert error.max() < tol, context


@pytest.mark.parametrize("order, dt, tol", [
    (2, 1e-2, 1e-5),
    (3, 5e-2, 1e-6),
])
def test_RungeKutta_pointMassWithPorts_pulling(point_mass_solution, order, dt, tol):
    """Same as test_RungeKutta_pointMassWithPorts, using a PointMassWithPort object
    as a child system, with pulled variables."""
    class SuperSystem(System):
        def setup(self):
            self.add_child(PointMassWithPorts("point"), pulling={
                "position": "pos",
                "kinematics": "kin",
                "mass": "mass",
                "k": "k",
            })

    make_case = case_factory(SuperSystem, "test")

    settings = dict(order=order, time_interval=(0, 2), dt=dt)
    system, driver = make_case(RungeKutta, **settings)

    includes = ['*.x', '*.v', '*.a']
    driver.add_recorder(DataFrameRecorder(includes=includes), period=0.1)

    x0 = [-1., 0., 10]
    v0 = [8, 0, 9.5]
    driver.set_scenario(
        init = {"pos.x": np.array(x0), "kin.v": np.array(v0)},
        values = {"mass": 1.5, "k": 0.5},
    )

    system.run_drivers()

    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    traj = np.asarray(data['pos.x'])
    solution = point_mass_solution(system.point, v0, x0)
    error = np.zeros(3)
    for t, x in zip(time, traj):
        error = np.maximum(error, rel_error(x, solution.x(t)))
    context = f"dt = {driver.dt}, order = {driver.order}"
    assert error.max() < tol, context


@pytest.mark.parametrize("dt, tol", [
    (1e-1, 5e-2),
    (1e-2, 5e-3),
])
def test_RungeKutta_rate_singleTimeStep(rate_case_1, dt, tol):
    settings = dict(order=2, time_interval=(0, dt), dt=dt)
    system, driver = rate_case_1(RungeKutta, **settings)
    context = f"dt = {driver.dt}, order = {driver.order}"
    assert driver.dt == driver.time_interval[1], context

    driver.set_scenario(values={'k': 1.9, 'U': 'exp(k * t)'})
    system.run_drivers()

    solution = lambda t: system.k * np.exp(system.k * t)
    assert system.k == 1.9
    assert system.dU_dt == pytest.approx(solution(dt), rel=tol) #, context


@pytest.mark.parametrize("dt, tol", [
    (1e-1, 5e-2),
    (1e-2, 5e-3),
])
def test_RungeKutta_rate(rate_case_1, dt, tol):
    settings = dict(order=2, time_interval=(0, 1), dt=dt)
    system, driver = rate_case_1(RungeKutta, **settings)
    context = f"dt = {driver.dt}, order = {driver.order}"

    driver.set_scenario(values={'k': 1.9, 'U': 'exp(k * t)'})

    driver.add_recorder(DataFrameRecorder(includes=['dU_dt']), period=0.1)

    system.run_drivers()

    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    result = np.asarray(data['dU_dt'], dtype=float)
    solution = lambda t: system.k * np.exp(system.k * t)
    error = 0
    for i, t in enumerate(time):
        exact = solution(t)
        dU_dt = result[i]
        error = max(error, rel_error(dU_dt, exact))
    assert error < tol, context


@pytest.mark.parametrize("parameters, settings, expected", [
    (dict(length=0.2, mass=0.6, K=20, c=1), dict(order=3, time_interval=[0, 8]), dict(tol=1e-5, dt=0.01732)),
    (dict(length=0.2, mass=0.6, K=20, c=1), dict(order=3, time_interval=[0, 8], dt=1e-2), dict(tol=1e-5)),
    (dict(length=0.2, mass=0.6, K=20, c=0), dict(order=3, time_interval=[0, 8], dt=1e-2), dict(tol=1e-4)),
    (dict(length=0.2, mass=0.6, K=20, c=0), dict(order=4, time_interval=[0, 8], dt=1e-2), dict(tol=1e-6)),
    (dict(length=0.2, mass=0.6, K=20, c=12), dict(order=3, time_interval=[0, 4], dt=1e-2), dict(tol=1e-5)),
    (dict(length=0.2, mass=4.5, K=20, c=1.2), dict(order=3, time_interval=[0, 8], dt=2e-2), dict(tol=2e-6)),
])
def test_RungeKutta_oscillator(oscillator_case, oscillator_solution, parameters, settings, expected):
    system, driver = oscillator_case(RungeKutta, **settings)

    driver.record_dt = auto_dt = driver.dt is None

    values = parameters.copy()
    x0 = values.pop('x0', 0.26)
    v0 = values.pop('v0', 0)
    driver.set_scenario(
        init = dict(x = x0, v = v0),
        values = values,
    )

    driver.add_recorder(DataFrameRecorder(includes=['x', 'v', 'a']), period=0.05)
    system.run_drivers()

    if auto_dt:  # time step deduced from system
        assert driver.recorded_dt.max() == pytest.approx(expected['dt'], rel=1e-3)
    else:
        assert driver.dt == settings['dt']

    solution = oscillator_solution(system, x0, v0)
    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    x = np.asarray(data['x'])
    error = 0
    for i, t in enumerate(time):
        error = max(error, abs(x[i] - solution.x(t)))

    assert error < expected['tol']


@pytest.mark.parametrize("parameters, settings, expected", [
    (dict(a=1, t0=3, tau=0.5), dict(order=3, dt=0.2, period=None), dict(tol=5e-4, dt_min=0.0825, dt_max=0.2)),
    (dict(a=1, t0=3, tau=0.5), dict(order=3, dt=0.1, period=None), dict(tol=1e-4, dt_min=0.0235, dt_max=0.1)),
    (dict(a=1, t0=3, tau=0.5), dict(order=4, dt=0.2, period=None), dict(tol=5e-5, dt_min=0.0825, dt_max=0.2)),
    # (dict(a=1, t0=3, tau=0.5, max_step=0.01), dict(order=3, dt=0.2, period=None), dict(tol=2e-4, dt_min=0.00825, dt_max=0.2)),  # TODO
])
def test_RungeKutta_gaussian(gaussian_ode, parameters, settings, expected):
    """
    The purpose of this test is mostly to check that the time step does not grow too quickly
    when the function's derivative rapidly decreases (which typically occurs at the tip of a
    steep Gaussian curve). Time step growth rate is controlled by driver option `max_dt_growth_rate`.
    """
    period = settings.pop('period', None)
    settings.setdefault('time_interval', [0, 2 * parameters['t0']])
    settings.setdefault('record_dt', True)
    settings.setdefault('max_dt_growth_rate', 1.5)

    f0 = 0
    ode = gaussian_ode
    driver = ode.make_case(RungeKutta, values=parameters.copy(), init=dict(f=f0), **settings)

    driver.add_recorder(
        # DSVRecorder(f'Gaussian_RK{driver.order}.csv', includes='f'),
        DataFrameRecorder(includes='f'),
        period=period
    )

    ode.run_drivers()
    # Retrieve recorded data and check accuracy
    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    result = np.asarray(data['f'], dtype=float)
    t0 = driver.time_interval[0]
    exact = ode.solution(time, init=(t0, f0))
    error = abs(result - exact)
    for var, value in parameters.items():
        assert (ode[var] == value), var
    assert error.max() < expected['tol']
    assert driver.recorded_dt.min() == pytest.approx(expected['dt_min'], rel=0.01)
    assert driver.recorded_dt.max() == pytest.approx(expected['dt_max'], rel=1e-9)


def test_RungeKutta_multimode_scalar_ode_1(multimode_scalar_ode_case):
    system, driver = multimode_scalar_ode_case(
        RungeKutta, order=2, time_interval=(0, 1), dt=0.1,
    )
    driver.add_recorder(DataFrameRecorder(includes=['f', 'df']), period=0.1)

    system.snap.trigger = "f > 0.347"

    driver.set_scenario(
        init = {'f': 0},
        values = {'df': '0 if snapped else 1'},
    )
    system.run_drivers()
    data = driver.recorder.export_data()

    assert system.f == pytest.approx(0.347, abs=1e-14)
    assert system.df == 0
    te = 0.347
    exact_t = np.r_[0, 0.1, 0.2, 0.3, te, te, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    exact_f = lambda t: np.where(t <= te, t, te)
    exact_df = lambda t: np.where(t <= te, 1.0, 0.0)
    expected = {
        'f': exact_f(exact_t),
        'df': exact_df(exact_t),
        'time': exact_t,
    }
    expected['df'][5] = 0.0  # discontinuity @ t = te
    assert np.asarray(data['time']) == pytest.approx(expected['time'], abs=1e-14)
    assert np.asarray(data['f']) == pytest.approx(expected['f'], abs=1e-14)
    assert np.asarray(data['df']) == pytest.approx(expected['df'], abs=1e-14)


def test_RungeKutta_multimode_scalar_ode_2(multimode_scalar_ode_case):
    system, driver = multimode_scalar_ode_case(
        RungeKutta, order=2, time_interval=(0, 1), dt=0.1,
    )
    driver.add_recorder(DataFrameRecorder(includes=['f', 'df']), period=0.1)

    system.snap.trigger = "f > 0.347"

    driver.set_scenario(
        init = {'f': 0},
        values = {'df': '0 if snapped else t'},
    )
    system.run_drivers()

    data = driver.recorder.export_data()
    # print(data)
    te = np.sqrt(2 * 0.347)
    exact_t = np.r_[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, te, te, 0.9, 1]
    exact_f = lambda t: np.where(t <= te, 0.5 * t**2, 0.5 * te**2)
    exact_df = lambda t: np.where(t <= te, t, 0.0)
    expected = {
        'f': exact_f(exact_t),
        'df': exact_df(exact_t),
        'time': exact_t,
    }
    expected['df'][-3] = 0.0  # discontinuity @ t = te
    assert system.f == pytest.approx(expected['f'][-1], abs=1e-14)
    assert system.df == 0
    assert np.asarray(data['time']) == pytest.approx(expected['time'], abs=1e-14)
    assert np.asarray(data['f']) == pytest.approx(expected['f'], abs=1e-14)
    assert np.asarray(data['df']) == pytest.approx(expected['df'], abs=1e-14)
