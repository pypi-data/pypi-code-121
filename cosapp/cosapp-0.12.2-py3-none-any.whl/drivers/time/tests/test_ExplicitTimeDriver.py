import pytest
from unittest.mock import MagicMock, patch

import logging
import re
import numpy as np

from cosapp.recorders import DataFrameRecorder
from cosapp.drivers.time import interfaces
from cosapp.drivers.time.interfaces import ExplicitTimeDriver
from cosapp.systems import System
from cosapp.utils.logging import LogFormat, LogLevel
from cosapp.utils.testing import rel_error, not_raised


@pytest.fixture(autouse=True)
def PatchExplicitTimeDriver():
    """Patch ExplicitTimeDriver to make it instanciable for tests"""
    patcher = patch.multiple(
        ExplicitTimeDriver,
        __abstractmethods__ = set(),
    )
    patcher.start()
    yield
    patcher.stop()


def test_ExplicitTimeDriver_init_default():
    driver = ExplicitTimeDriver()
    assert driver.name == "Explicit time driver"
    assert driver.owner is None
    assert driver.dt is None
    assert driver.time_interval is None


@pytest.mark.parametrize("settings, expected", [
    (dict(), dict()),
    (dict(name="John Doe"), dict(name="John Doe")),
    (dict(time_interval=(0, 1)), dict(time_interval=(0, 1))),
    (dict(dt=0.1, time_interval=(0, 1)), dict(dt=0.1, time_interval=(0, 1))),
    (dict(dt=0.1), dict(dt=0.1)),
    (dict(dt=1), dict(dt=1)),
    (dict(dt=0), dict(error=ValueError)),
    (dict(dt=-0.1), dict(error=ValueError)),
    (dict(dt="0.1"), dict(error=TypeError)),
    (dict(time_interval=(2, 1)), dict(error=ValueError)),
    (dict(time_interval=(1, 2, 3)), dict(error=ValueError)),
    (dict(time_interval=2.5), dict(error=TypeError)),
])
def test_ExplicitTimeDriver_init_args(settings, expected):
    error = expected.get('error', None)
    if error is None:
        driver = ExplicitTimeDriver(**settings)
        assert driver.dt == expected.get('dt', None)
        assert driver.time_interval == expected.get('time_interval', None)
        assert driver.name == expected.get('name', 'Explicit time driver')
    else:
        with pytest.raises(error):
            ExplicitTimeDriver(**settings)


@pytest.mark.parametrize("value, expected", [
    (10, dict(value=10)),
    (1e-2, dict(value=1e-2)),
    (1e-12, dict(value=1e-12)),
    (0, dict(error=ValueError, match="dt.*invalid value")),
    (-0.5, dict(error=ValueError, match="dt.*invalid value")),
    ("0.5", dict(error=TypeError, match="got str")),
])
def test_ExplicitTimeDriver_dt(value, expected):
    driver = ExplicitTimeDriver()
    assert driver.dt is None

    error = expected.get('error', None)
    if error is None:
        driver.dt = value
        assert driver.dt == expected['value']
    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            driver.dt = value


@pytest.mark.parametrize("value, expected", [
    ((0, 1), dict(value=(0, 1))),
    ([0, 1], dict(value=(0, 1))),
    ((0.2, 0.2), dict(value=(0.2, 0.2))),
    ((1, 1.5), dict(value=(1, 1.5))),
    ((-0.5, 0), dict(error=ValueError, match="start time")),
    (('0', 0.2), dict(error=TypeError, match="start time")),
    ((0.2, 0.1), dict(error=ValueError, match="end time")),
    ((0, np.inf), dict(error=ValueError, match="end time")),
    ((0, '0.5'), dict(error=TypeError, match="end time")),
    ((1, 2, 3), dict(error=ValueError, match="time_interval.*invalid")),
    (2.5, dict(error=TypeError, match="got float")),
    ("lifetime", dict(error=TypeError, match="got str")),
])
def test_ExplicitTimeDriver_time_interval(value, expected):
    driver = ExplicitTimeDriver()
    assert driver.time_interval is None

    error = expected.get('error', None)
    if error is None:
        driver.time_interval = value
        assert driver.time_interval == expected['value']
    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            driver.time_interval = value


@pytest.mark.parametrize("dt, expected", [(1e-2, 1e-2), (0.1, 0.02), (None, 0.02)])
def test_ExplicitTimeDriver_limit_dt(ode_case_1, dt, expected):
    ode, driver = ode_case_1(ExplicitTimeDriver, time_interval=[0, 0.1], record_dt=True)
    if dt is not None:
        driver.dt = dt
        assert driver.dt == dt
    else:
        assert driver.dt is None
    ode.tau = 0.1
    ode.run_drivers()
    comment = "Time step should be limited by transient max_time_step"
    assert driver.recorded_dt.min() == pytest.approx(expected, rel=1e-12), comment
    assert driver.recorded_dt.max() == pytest.approx(expected, rel=1e-12), comment


@pytest.mark.parametrize("scenario, ok", [
    # constant value of f.max_time_step
    (dict(values={'sub2.y': 10}), True),
    (dict(values={'sub2.y': 0}), False),
    (dict(values={'sub2.y': -0.1}), False),
    # non-const max_time_step
    (dict(values={'sub2.y': '1 if t < 0.2 else -1'}, time_interval=(0, 0.3)), False),
    (dict(values={'sub2.y': '1 if t < 0.5 else -1'}, time_interval=(0, 0.3)), True),
])
def test_ExplicitTimeDriver_dt_RuntimeError(scenario, ok):
    """
    Check that time driver raises RuntimeError when the maximum time step of
    one of the transients is not strictly positive at the beginning of time loop.
    """
    class SubSystem(System):
        def setup(self):
            self.add_inward('x', 1.0)
            self.add_inward('y', 1.0)

    class DynamicSystem(System):
        def setup(self):
            self.add_child(SubSystem('sub1'))
            self.add_child(SubSystem('sub2'))

            self.add_transient('f', der='sub1.x * sub1.y', max_time_step='0.5 * sub2.y')

    # set driver settings
    settings = dict(dt=0.1, time_interval=[0, 0.2])  # default
    for setting in settings:
        try:
            settings[setting] = scenario.pop(setting)
        except KeyError:
            continue

    s = DynamicSystem('s')
    driver = s.add_driver(ExplicitTimeDriver(**settings))
    driver.set_scenario(**scenario)

    if ok:
        try:
            s.run_drivers()
        except RuntimeError:
            pytest.fail("Should not raise RuntimeError")
    else:
        with pytest.raises(RuntimeError, match="non-positive value"):
            s.run_drivers()


def test_ExplicitTimeDriver_set_time_before_System_setup():

    start_t = 24.
    end_t = 25.

    class DummySystem(System):
        def setup_run(self):
            nonlocal start_t
            assert self.time == start_t

    driver = ExplicitTimeDriver()
    system = DummySystem('dummy')

    system.add_driver(driver)

    driver.time_interval = (start_t, end_t)
    driver.dt = end_t - start_t
    # Check that the start time is set as the clock time
    system.run_drivers()

    start_t = 5.0
    # Check that the new start time is set as the clock time
    driver.time_interval = (start_t, start_t + driver.dt)
    system.run_drivers()


def test_ExplicitTimeDriver_is_standalone():
    driver = ExplicitTimeDriver()
    assert driver.is_standalone()


def test_ExplicitTimeDriver_ode_run_driver(ode_case_1):
    ode, driver = ode_case_1(ExplicitTimeDriver, record_dt=True)
    assert driver.owner is ode
    assert driver.dt is None
    assert driver.time_interval is None
    with pytest.raises(ValueError, match="Time interval.*not specified"):
        ode.run_drivers()
    driver.time_interval = (0, 1)
    assert driver.dt is None
    ode.tau = 0.1
    ode.run_drivers()
    # Check that time step was set by max_time_step of transient 'ode.f'
    assert driver.recorded_dt.min() == pytest.approx(0.02, rel=1e-12)
    assert driver.recorded_dt.max() == pytest.approx(0.02, rel=1e-12)

    ode, driver = ode_case_1(ExplicitTimeDriver, dt=1e-2)
    assert driver.owner is ode
    assert driver.dt == 1e-2
    assert driver.time_interval is None
    with pytest.raises(ValueError, match="Time interval.*not specified"):
        ode.run_drivers()

    ode, driver = ode_case_1(ExplicitTimeDriver, dt=1e-2, time_interval=[0, 1])
    assert driver.owner is ode
    assert driver.dt == 1e-2
    assert driver.time_interval == (0, 1)


def test_ExplicitTimeDriver_dt_None():
    """Expected behaviour:
    ValueError exception raised when driver.dt is None, and `max_time_step` is not given by system transients"""
    class PlainSystem(System):
        def setup(self):
            self.add_inward('a', 1.0)
            self.add_transient('A', der='a')  # max_time_step unspecified

    system = PlainSystem('plain')
    driver = system.add_driver(ExplicitTimeDriver(time_interval=(0, 1)))
    assert driver.dt is None
    assert driver.time_interval == (0, 1)
    with pytest.raises(ValueError, match="Time step.*not specified.*and could not be determined from transient variables"):
        system.run_drivers()


def test_ExplicitTimeDriver_ode_add_scenario(ode_case_1):
    ode, driver = ode_case_1(ExplicitTimeDriver)
    driver.set_scenario()
    assert driver.scenario.name == "scenario"
    assert driver.scenario.context is ode
    driver.set_scenario("test")
    assert driver.scenario.name == "test"
    assert driver.scenario.context is ode
    driver.set_scenario("final")
    assert driver.scenario.name == "final"
    assert driver.scenario.context is ode


@pytest.mark.parametrize("driver_settings, period, expected", [
    (dict(), None, dict(period=None)),
    (dict(), 0.1, dict(period=0.1)),
    (dict(dt=1e-2), None, dict(period=None)),
    (dict(time_interval=[0, 2]), 0.1, dict(period=0.1)),
    (dict(dt=1e-1, time_interval=[0, 2]), 0.01, dict(period=0.01)),
    (dict(dt=1e-2, time_interval=[0, 2]), 0.1, dict(period=0.1)),
    (dict(dt=1e-2, time_interval=[0, 2]), 1, dict(period=1)),
    (dict(dt=1e-2, time_interval=[0, 2]), 100, dict(period=2)),
    (dict(dt=1e-2, time_interval=[0, 2]), 0, dict(error=ValueError, match="period.* invalid value")),
    (dict(dt=1e-2, time_interval=[0, 2]), -1, dict(error=ValueError, match="period.* invalid value")),
    (dict(dt=1e-2, time_interval=[0, 2]), '0.1', dict(error=TypeError)),
])
def test_ExplicitTimeDriver_add_recorder(two_tank_case, driver_settings, period, expected):
    """Test `add_recorder` method before driver execution"""
    system, driver = two_tank_case(ExplicitTimeDriver, **driver_settings)
    assert driver.recorder is None

    rec_options = dict(includes='tank?.height')
    error = expected.get('error', None)

    if error is None:
        driver.add_recorder(DataFrameRecorder(**rec_options), period)
        assert driver.recording_period == expected['period']
        assert driver.recorder is not None
        assert 'time' in driver.recorder.field_names()

    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            driver.add_recorder(DataFrameRecorder(**rec_options), period)


@pytest.mark.parametrize("driver_settings, period, expected", [
    (dict(), None, dict(error=ValueError, match="Time interval was not specified")),
    (dict(), 0.1, dict(error=ValueError, match="Time interval was not specified")),
    (dict(dt=1e-2), None, dict(error=ValueError, match="Time interval was not specified")),
    (dict(time_interval=[0, 2]), 0.1, dict(period=0.1)),
    (dict(time_interval=[0, 2]), None, dict(period=None, warnings=["all time steps will be recorded"])),
    (dict(dt=1e-1, time_interval=[0, 2]), 0.01, dict(period=0.01)),
    (dict(dt=1e-2, time_interval=[0, 2]), 0.1, dict(period=0.1)),
    (dict(dt=1e-2, time_interval=[0, 2]), 1, dict(period=1)),
    (dict(dt=1e-2, time_interval=[0, 2]), 100, dict(period=2)),
])
def test_ExplicitTimeDriver_recorder(ode_case_1, caplog, driver_settings, period, expected):
    """Test recorder behaviour during driver execution, assuming `add_recorder` is correct"""
    system, driver = ode_case_1(ExplicitTimeDriver, **driver_settings)

    driver.add_recorder(DataFrameRecorder(includes='*'), period)
    driver.set_scenario(init={'f': 0}, values={'tau': 0.5})

    error = expected.get('error', None)

    if error is None:
        # run simulation and capture potential warnings
        caplog.clear()
        with caplog.at_level(logging.WARNING, logger=interfaces.__name__):
            system.run_drivers()

        assert driver.recording_period == expected['period']

        warnings = expected.get('warnings', [])
        assert len(caplog.records) == len(warnings)
        for warning, record in zip(warnings, caplog.records):
            assert warning in record.message
    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            system.run_drivers()


@pytest.mark.parametrize("dt, tol", [
    (1e-1, 1e-1),
    (1e-2, 1e-2),
])
def test_ExplicitTimeDriver_rate_singleTimeStep(rate_case_1, dt, tol):
    settings = dict(time_interval=(0, dt), dt=dt)
    system, driver = rate_case_1(ExplicitTimeDriver, **settings)
    assert driver.dt == driver.time_interval[1]

    driver.set_scenario(
        values = {'k': 1.5, 'U': 'exp(k * t)'}
    )
    system.run_drivers()

    assert system.k == 1.5
    solution = lambda t: system.k * np.exp(system.k * t)
    assert system.dU_dt == pytest.approx(solution(dt), rel=tol)


@pytest.mark.parametrize("dt, tol", [
    (1e-1, 1e-1),
    (1e-2, 1e-2),
])
def test_ExplicitTimeDriver_rate(rate_case_1, dt, tol):
    settings = dict(time_interval=(0, 1), dt=dt)
    system, driver = rate_case_1(ExplicitTimeDriver, **settings)

    driver.set_scenario(
        values = {'k': 1.5, 'U': 'exp(k * t)'}
    )
    driver.add_recorder(DataFrameRecorder(includes=['dU_dt']), period=0.1)

    system.run_drivers()

    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    exact = system.k * np.exp(system.k * time)
    error = rel_error(data['dU_dt'], exact)
    assert error.max() < tol


def test_ExplicitTimeDriver_rate_no_initial_value():
    """
    Same as `test_ExplicitTimeDriver_rate`, except rate `dU_dt`
    is not given any initial value.
    This test checks that `dU_dt` is correctly set by an explicit
    initial condition in `set_scenario`.
    Note: fixes bug reported in issue #193, "Bug in rate initialization".
    """
    class RateSystem(System):
        def setup(self):
            self.add_inward("k", 1.0)
            self.add_inward("U", 0.0)
            self.add_rate("dU_dt", source="U")

    system = RateSystem("system")
    driver = system.add_driver(ExplicitTimeDriver(time_interval=(0, 0.1), dt=0.1))

    driver.set_scenario(
        init = {'dU_dt': 'k'},
        values = {
            'U': 'exp(k * t)',
            'k': -3.6,  # should initialize `dU_dt`
        }
    )

    driver.add_recorder(DataFrameRecorder(includes=['dU_dt']))

    system.run_drivers()

    data = driver.recorder.export_data()
    result = np.asarray(data['dU_dt'], dtype=float)
    assert system.k == -3.6
    assert result[0] == system.k
    assert result[1] == pytest.approx((np.exp(system.k * driver.dt) - 1) / driver.dt, rel=1e-14)


@pytest.mark.parametrize("options, recorder_period, expected", [
    (dict(), 0.1, dict(period=0.1)),
    (dict(dt=1e-2), None, dict(period=None)),
    (dict(dt=1e-2, time_interval=[0, 2]), 0.1, dict(period=0.1)),
    (dict(dt=1e-1, time_interval=[0, 2]), 1, dict(period=1)),
    (dict(dt=1e-1, time_interval=[0, 2]), 100, dict(period=2)),
])
def test_ExplicitTimeDriver_recorded_times(two_tank_case, options, recorder_period, expected):
    driver_settings = dict(dt=1e-1, time_interval=[0, 1])
    driver_settings.update(options)
    system, driver = two_tank_case(ExplicitTimeDriver, **driver_settings)

    driver.add_recorder(DataFrameRecorder(includes='tank1.height'), recorder_period)

    system.run_drivers()

    period = driver.recording_period
    assert period == expected['period']
    t0, tn = driver.time_interval
    data = driver.recorder.export_data()
    time = np.asarray(data['time'])
    if period is not None:
        assert time == pytest.approx(np.arange(t0, tn + period / 2, period), abs=1e-12)


@pytest.mark.parametrize("format", LogFormat)
@pytest.mark.parametrize("msg, kwargs, to_log, emitted", [
    ("zombie call_setup_run", dict(), False, None),
    ("useless start call_clean_run", dict(activate=True), False, None),
    (
        f"{System.CONTEXT_EXIT_MESSAGE} call_clean_run",
        dict(activate=False),
        False,
        dict(levelno=LogLevel.DEBUG, pattern=r"Compute calls for [\w\.]+: \d+")
    ),
    (
        "other message with activation",
        dict(activate=True),
        False,
        None,
    ),
    (
        "second message with deactivation",
        dict(activate=False),
        False, 
        dict(levelno=LogLevel.FULL_DEBUG, pattern=r"Time steps:\n")
    ),
    ("common message", dict(), True, None),
])
def test_ExplicitTimeDriver_log_debug_message(format, msg, kwargs, to_log, emitted):
    # Attribute of a mock object can be created by passing them as kwargs.
    # Here, we get an object in the variable handler with two members:
    # an attribute level == LogLevel.DEBUG and an mocked attribute log
    handler = MagicMock(level=LogLevel.DEBUG, log=MagicMock())
    rec = logging.getLogRecordFactory()("log_test", LogLevel.INFO, __file__, 22, msg, (), None)
    for key, value in kwargs.items():
        setattr(rec, key, value)

    d = ExplicitTimeDriver("dummy")

    assert d.log_debug_message(handler, rec, format) == to_log

    if "activate" in kwargs and not msg.endswith("_run"):
        assert d.record_dt == kwargs["activate"]

    if emitted:
        handler.log.assert_called_once()
        args = handler.log.call_args[0]
        assert args[0] == emitted["levelno"]
        assert re.match(emitted["pattern"], args[1]) is not None
    else:
        handler.log.assert_not_called()


def test_ExplicitTimeDriver_init_conditions():
    """
    Test checking that initial conditions are applied before any system compute.
    Related to https://gitlab.com/cosapp/cosapp/-/issues/20
    """
    class Dummy(System):
        def setup(self):
            self.add_inward('c', 1.0)
            self.add_transient('x', der='c - c')

        def compute(self):
            if self.x <= 0:
                raise RuntimeError("x must be positive")
            if self.c >= 0:
                raise RuntimeError("c must be negative")

    system = Dummy('dummy')
    driver = system.add_driver(ExplicitTimeDriver(dt=0.1, time_interval=[0, 0.1]))

    driver.set_scenario(
        init = {'x': 1.0},  # valid initial value for x
        values = {'c': '-(1 + t**2)'},  # valid c(t) value
    )

    system.x = system.c = -1.0
    with pytest.raises(RuntimeError, match="x must be positive"):
        system.run_once()

    system.x = system.c = 1.0
    with pytest.raises(RuntimeError, match="c must be negative"):
        system.run_once()

    system.c, system.x = 1.0, -1.0  # both invalid
    with pytest.raises(RuntimeError):
        system.run_once()
    
    # Running the time driver should not raise RuntimeError,
    # as both x and c are expected to be set at valid values
    with not_raised(RuntimeError):
        system.run_drivers()

    assert system.x == 1
    assert system.c == pytest.approx(-1.01)
