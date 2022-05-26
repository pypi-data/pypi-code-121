import pytest
import logging, re
import numpy as np

from cosapp.base import Port, System
from cosapp.drivers import EulerExplicit
from cosapp.drivers.time.scenario import Scenario, Interpolator
from cosapp.core.eval_str import AssignString
from cosapp.multimode.event import Event
from cosapp.core.time import UniversalClock


@pytest.fixture
def clock():
    clock = UniversalClock()
    yield clock
    clock.time = 0


class XyzPort(Port):
    def setup(self):
        self.add_variable('x')
        self.add_variable('y')
        self.add_variable('z')


class AbcdPort(Port):
    def setup(self):
        self.add_variable('a')
        self.add_variable('b')
        self.add_variable('c')
        self.add_variable('d')


class XySystem(System):
    def setup(self):
        self.add_input(XyzPort, 'x_in')
        self.add_output(XyzPort, 'x_out')


class AbcdSystem(System):
    def setup(self):
        self.add_inward('x')
        self.add_outward('y')
        self.add_inward('v', np.ones(5))
        self.add_input(AbcdPort, 'a_in')
        self.add_output(AbcdPort, 'a_out')


@pytest.fixture
def assembly():
    """Unconnected assembly of `XySystem` and `AbcdSystem` components"""
    head = System('head')
    head.add_child(XySystem('foo1'), pulling='x_in')
    head.add_child(XySystem('foo2'))
    head.add_child(AbcdSystem('bar1'), pulling={'v': 'theta'})
    head.add_child(AbcdSystem('bar2'), pulling={'x': 'alpha', 'a_out': 'a_out'})

    return head


@pytest.fixture(scope='function')
def case(two_tank_case):
    return two_tank_case(EulerExplicit, dt=0.1, time_interval=[0, 1])


@pytest.fixture(scope='function')
def scenario(case):
    driver = case[1]
    return Scenario('scenario', driver)


@pytest.fixture(scope='function')
def varying_mu_case(case):
    """Two-tank test case with exponentially decaying viscosity"""
    system, driver = case

    mu_0, mu_inf, tau = 1e-2, 2e-3, 200  # viscosity parameters
    mu = lambda t: mu_inf + (mu_0 - mu_inf) * np.exp(-t / tau)

    scenario = Scenario.make('scenario',
        driver = driver,
        init = {
            'tank1.height': '10 * pipe.D',
            'tank2.height': 'tank1.height + 1',
        },
        values = {
            'pipe.D': 0.3,
            'tank1.area': '5',
            'pipe.L': '50 * pipe.D',
            'pipe.mu': f'{mu_inf} + ({mu_0} - {mu_inf}) * exp(-t / {tau})',
        },
    )
    return system, driver, scenario, mu


def test_Scenario__init__(case):
    system, driver = case
    scenario = Scenario('scenario', driver)
    assert scenario.owner is driver
    assert scenario.context is system
    assert scenario.init_values == []
    assert scenario.case_values == []
    assert isinstance(scenario.stop, Event)
    assert scenario.stop.final
    with pytest.raises(TypeError):
        scenario.owner = 'foo'


def test_Scenario_stop(case):
    system, driver = case
    
    scenario = Scenario('scenario', driver)
    assert isinstance(scenario.stop, Event)
    scenario.stop.trigger = 'tank1.height <= 0'
    assert scenario.stop.context is system
    assert scenario.stop.final
    assert scenario.stop.is_primitive

    scenario = Scenario('scenario', driver)
    scenario.stop.trigger = Event.merge(
        Event('e1', system, trigger='tank1.height == 0'),
        Event('e2', system, trigger='tank2.height > 10'),
    )
    assert scenario.stop.context is system
    assert scenario.stop.final
    assert not scenario.stop.is_primitive
    
    with pytest.raises(AttributeError, match="can't set attribute"):
        scenario.stop = 'foo'


@pytest.mark.parametrize("init, expected", [
    (
        {'tank1.height': 1.2, 'tank2.height': 0.5},
        dict(content=['tank1.height = 1.2', 'tank2.height = 0.5'], n_const=2)
    ),
    (
        {'tank2.height': 0.5, 'tank1.height': 1.2},
        dict(content=['tank1.height = 1.2', 'tank2.height = 0.5'], n_const=2)
    ),
    (
        {'tank2.height': 'tank1.height + 1', 'tank1.height': 2, },
        dict(content=['tank1.height = 2', 'tank2.height = tank1.height + 1'], n_const=1)
    ),
    (
        {'tank1.height': '10 * pipe.D', 'tank2.height': 0.5, },
        dict(content=['tank2.height = 0.5', 'tank1.height = 10 * pipe.D'], n_const=1)
    ),
    (
        {'tank1.height': 'exp(1.5)', 'tank2.height': '10 * pipe.D', 'pipe.D': 0.25},
        dict(content=['pipe.D = 0.25', 'tank1.height = exp(1.5)', 'tank2.height = 10 * pipe.D'], n_const=2)
    ),
    (
        {'tank1.height': 'pipe.L / 2', 'tank2.height': '10 * pipe.D', 'pipe.D': 0.25},
        dict(content=['pipe.D = 0.25', 'tank1.height = pipe.L / 2', 'tank2.height = 10 * pipe.D'], n_const=1)
    ),
    (
        {'tank1.height': 'pipe.L / 2', 'tank2.height': '10 * pipe.D'},
        dict(content=['tank1.height = pipe.L / 2', 'tank2.height = 10 * pipe.D'], n_const=0)
    ),
    # Erroneous cases:
    ({'foo.bar': 2}, dict(error=AttributeError, match=r"'foo\.bar' is not known in system")),
    ({'pipe.k': 2}, dict(error=ValueError, match="Only variables in input ports can be used as boundaries")),
])
def test_Scenario_set_init(scenario, init, expected):
    error = expected.get('error', None)

    if error is None:
        scenario.set_init(init)
        assert all(isinstance(assignment, AssignString) for assignment in scenario.init_values)

        n_const = expected['n_const']
        content = expected['content']
        const = content[:n_const]
        nonconst = content[n_const:]
        init_conds = [str(assignment) for assignment in scenario.init_values]
        # First elements, expected to be constants init_conds 
        assert len(init_conds[:n_const]) == n_const
        assert set(init_conds[:n_const]) == set(const)
        assert all(assignment.constant for assignment in scenario.init_values[:n_const])
        # End init_conds (unordered, from dict entry)
        assert len(init_conds[n_const:]) == len(nonconst)
        assert set(init_conds[n_const:]) == set(nonconst)

    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            scenario.set_init(init)


@pytest.mark.parametrize("values, expected", [
    (
        {'pipe.D': 0.3, 'pipe.L': '5'},
        dict(init=['pipe.L = 5', 'pipe.D = 0.3'], values=[],)
    ),
    (
        {'pipe.D': 0.3, 'pipe.L': '50 * pipe.D'},
        dict(init=['pipe.D = 0.3'], values=['pipe.L = 50 * pipe.D'],)
    ),
    (
        {
            'tank1.area': 2,
            'pipe.D': 0.3,
            'pipe.L': '50 * pipe.D',
            'pipe.mu': '{vinf} + ({v0} - {vinf}) * exp(-t / {tau})'.format(v0=1e-2, vinf=2e-3, tau=200),
        },
        dict(
            init=['pipe.D = 0.3', 'tank1.area = 2'],
            values=[
                'pipe.L = 50 * pipe.D',
                'pipe.mu = {vinf} + ({v0} - {vinf}) * exp(-t / {tau})'.format(v0=1e-2, vinf=2e-3, tau=200)
            ],
        )
    ),
    # Erroneous cases:
    ({'foo.bar': 2}, dict(error=AttributeError, match=r"'foo\.bar' is not known in system")),
    ({'pipe.k': 2}, dict(error=ValueError, match="Only variables in input ports can be used as boundaries")),
])
def test_Scenario_set_values(scenario, values, expected):
    error = expected.get('error', None)

    if error is None:
        scenario.set_values(values)
        assert all(isinstance(assignment, AssignString) for assignment in scenario.case_values)
        assert all(not assignment.constant for assignment in scenario.case_values)

        init_conds = [str(assignment) for assignment in scenario.init_values]
        time_conds = [str(assignment) for assignment in scenario.case_values]

        # Test time-dependent boundary conditions
        assert set(time_conds) == set(expected['values'])
        assert set(init_conds) == set(expected['init'])

    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            scenario.set_values(values)


def test_Scenario_add_init(case):
    system, driver = case

    scenario = Scenario.make('scenario',
        driver = driver,
        values = {},
        init = {
            'tank1.height': '10 * pipe.D',
        },
    )
    assert len(scenario.init_values) == 1
    assert str(scenario.init_values[0]) == 'tank1.height = 10 * pipe.D'

    scenario.add_init({'tank2.height': 'tank1.height + 1'})
    assert len(scenario.init_values) == 2
    assert str(scenario.init_values[1]) == 'tank2.height = tank1.height + 1'

    scenario.add_init({'tank2.area': '1.3'})
    assert len(scenario.init_values) == 3
    assert str(scenario.init_values[0]) == 'tank2.area = 1.3'
    assert str(scenario.init_values[1]) == 'tank1.height = 10 * pipe.D'
    assert str(scenario.init_values[2]) == 'tank2.height = tank1.height + 1'


def test_Scenario_add_values(case):
    system, driver = case
    mu_0, mu_inf, tau = 1e-2, 2e-3, 200

    scenario = Scenario.make('scenario',
        driver = driver,
        values = {
            'tank1.area': '5',  # constant
            'pipe.D': 0.3,      # constant
            'pipe.mu': f'{mu_inf} + ({mu_0} - {mu_inf}) * exp(-t / {tau})',
        },
        init = {
            'tank1.height': '10 * pipe.D',
            'tank2.height': 'tank1.height + 1',
        },
    )

    assert len(scenario.init_values) == 4
    assert len(scenario.case_values) == 1

    init_conds = [str(assignment) for assignment in scenario.init_values]
    assert set(init_conds[:2]) == {'tank1.area = 5', 'pipe.D = 0.3'}
    assert set(init_conds[2:]) == {
        'tank1.height = 10 * pipe.D',
        'tank2.height = tank1.height + 1'
    }

    case_conds = [str(assignment) for assignment in scenario.case_values]
    assert set(case_conds) == {
            f'pipe.mu = {mu_inf} + ({mu_0} - {mu_inf}) * exp(-t / {tau})',
    }

    # Add non-const boundary condition
    scenario.add_values({'tank2.area': '10 * pipe.D**2'})
    assert len(scenario.init_values) == 4
    assert len(scenario.case_values) == 2
    assert str(scenario.case_values[-1]) == 'tank2.area = 10 * pipe.D**2'

    # Add constant boundary condition
    scenario.add_values({'pipe.L': 3.4})
    assert len(scenario.init_values) == 5
    assert len(scenario.case_values) == 2
    assert str(scenario.init_values[0]) == 'pipe.L = 3.4'


def test_Scenario_add_values_tabulated(case):
    system, driver = case
    mu_0, mu_inf, tau = 1e-2, 2e-3, 200

    scenario = Scenario.make('scenario',
        driver = driver,
        values = {
            'tank1.area': '5',  # constant
            'pipe.D': 0.3,      # constant
            'pipe.mu': Interpolator(data=[(0, mu_0), (1, mu_0), (1.1, mu_inf), (1000, mu_inf)]),
        },
        init = {
            'tank1.height': '10 * pipe.D',
            'tank2.height': 'tank1.height + 1',
        },
    )

    assert len(scenario.init_values) == 4
    assert len(scenario.case_values) == 1

    init_conds = [str(assignment) for assignment in scenario.init_values]
    assert set(init_conds[:2]) == {'tank1.area = 5', 'pipe.D = 0.3'}
    assert set(init_conds[2:]) == {
        'tank1.height = 10 * pipe.D',
        'tank2.height = tank1.height + 1'
    }

    case_conds = [str(assignment) for assignment in scenario.case_values]
    assert set(case_conds) == {
            'pipe.mu = Interpolator(t)',
    }


@pytest.mark.parametrize("case_data, expected", [
    (
        dict(
            init = {'tank1.height': '10 * pipe.D', 'tank2.height': 'tank1.height + 1'},
            values = {'pipe.D': 0.3, 'tank1.area': '5'},
        ),
        dict(
            init = dict(
                content=[
                    'pipe.D = 0.3', 'tank1.area = 5',  # const assignments passed as init conditions
                    'tank1.height = 10 * pipe.D', 'tank2.height = tank1.height + 1'
                ],
                n_const=2
            ),
            values = [],
        )
    ),
    (
        dict(
            init = {'tank1.height': '10 * pipe.D', 'tank2.height': 'tank1.height + 1'},
            values = {
                'pipe.D': 0.3,
                'tank1.area': '5',
                'pipe.L': '50 * pipe.D',
                'pipe.mu': '{vinf} + ({v0} - {vinf}) * exp(-t / {tau})'.format(v0=1e-2, vinf=2e-3, tau=200),
            },
        ),
        dict(
            init = dict(
                content=[
                    'pipe.D = 0.3', 'tank1.area = 5',  # const assignments passed as init conditions
                    'tank1.height = 10 * pipe.D', 'tank2.height = tank1.height + 1'
                ],
                n_const=2
            ),
            values = [
                'pipe.L = 50 * pipe.D',
                'pipe.mu = {vinf} + ({v0} - {vinf}) * exp(-t / {tau})'.format(v0=1e-2, vinf=2e-3, tau=200),
            ],
        )
    ),
])
def test_Scenario_factory(case, case_data, expected):
    system, driver = case
    scenario = Scenario.make('scenario',
        driver = driver,
        init = case_data['init'],
        values = case_data['values'],
    )

    assert scenario.owner is driver
    assert scenario.context is system
    assert isinstance(scenario, Scenario)
    assert all(isinstance(assignment, AssignString) for assignment in scenario.init_values)
    assert all(isinstance(assignment, AssignString) for assignment in scenario.case_values)
    assert all(assignment.eval_context is system for assignment in scenario.init_values)
    assert all(assignment.eval_context is system for assignment in scenario.case_values)

    init_conds = [str(assignment) for assignment in scenario.init_values]
    time_conds = [str(assignment) for assignment in scenario.case_values]

    # Test time-dependent boundary conditions
    assert set(time_conds) == set(expected['values'])

    # Test initial conditions
    content = expected['init']['content']
    n_const = expected['init']['n_const']
    const = content[:n_const]
    nonconst = content[n_const:]
    # First elements, expected to be constants init_conds 
    assert len(init_conds[:n_const]) == n_const
    assert set(init_conds[:n_const]) == set(const)
    assert all(assignment.constant for assignment in scenario.init_values[:n_const])
    # End init_conds (unordered, from dict entry)
    assert len(init_conds[n_const:]) == len(nonconst)
    assert set(init_conds[n_const:]) == set(nonconst)


def test_Scenario_apply_values(varying_mu_case, set_master_system):
    """Test methods `apply_init_values()` and `update_values()`"""
    system, driver, scenario, mu = varying_mu_case

    system.tank1.height = system.tank2.height = 1
    system.tank1.area = system.tank2.area = 1
    system.pipe.D = 1
    system.pipe.L = 1
    system.pipe.mu = 0.1

    scenario.apply_init_values()
    assert system.pipe.D == 0.3
    assert system.tank1.height == 3
    assert system.tank2.height == 4
    assert system.tank1.area == 5
    assert system.tank2.area == 1
    # Check that non-const boundary conditions have not been applied yet
    assert system.pipe.L == 1
    assert system.pipe.mu == 0.1

    # Apply time-dependent boundary conditions
    driver._set_time(0.)
    assert system.time == 0
    scenario.update_values()
    assert system.pipe.L == 15
    assert system.pipe.mu == mu(system.time)

    driver._set_time(10.)
    assert system.time == 10
    scenario.update_values()
    assert system.pipe.L == 15
    assert system.pipe.mu == mu(system.time)


def test_Scenario_clear_init(varying_mu_case):
    scenario = varying_mu_case[2]
    assert len(scenario.init_values) == 4
    assert len(scenario.case_values) == 2
    
    scenario.clear_init()
    assert len(scenario.init_values) == 0
    assert len(scenario.case_values) == 2


def test_Scenario_clear_values(varying_mu_case):
    scenario = varying_mu_case[2]
    assert len(scenario.init_values) == 4
    assert len(scenario.case_values) == 2
    
    scenario.clear_values()
    assert len(scenario.init_values) == 4
    assert len(scenario.case_values) == 0


def test_Scenario_aliasing_0(assembly, caplog):
    head = assembly
    driver = head.add_driver(EulerExplicit('driver'))

    scenario = Scenario('scenario', driver)

    with caplog.at_level(logging.INFO):
        scenario.set_init({
            'foo1.x_in.z': 1.3,
            'x_in.x': 'x_in.z + 1',
            'bar2.x': 0.1,  # pulled as `alpha`
        })
        scenario.set_values({
            'foo1.x_in.x': '2 * cos(t)',
            'foo1.x_in.y': Interpolator(data=[(0, 0), (5, -2), (1000, 500)]),
            'foo2.x_in.x': 'exp(-t / 4) * foo1.x_in.y',
            'bar1.v[::2]': '[0.1 * t, 0.2, 0.3]',  # pulled as `theta`
        })
    assert len(caplog.records) == 5
    assert re.match(
        "Replace 'foo1.x_in.z' by 'x_in.z'",
        caplog.records[0].message
    )
    assert re.match(
        "Replace 'bar2.x' by 'alpha'",
        caplog.records[1].message
    )
    assert re.match(
        "Replace 'foo1.x_in.x' by 'x_in.x'",
        caplog.records[2].message
    )
    assert re.match(
        "Replace 'foo1.x_in.y' by 'x_in.y'",
        caplog.records[3].message
    )
    assert re.match(
        "Replace 'bar1.v' by 'theta'",
        caplog.records[4].message
    )
    
    init_conds = map(str, scenario.init_values)
    time_conds = map(str, scenario.case_values)

    assert set(init_conds) == {
        'x_in.z = 1.3',
        'x_in.x = x_in.z + 1',
        'alpha = 0.1',
    }
    assert set(time_conds) == {
        'x_in.x = 2 * cos(t)',
        'x_in.y = Interpolator(t)',
        'foo2.x_in.x = exp(-t / 4) * foo1.x_in.y',
        'theta[::2] = [0.1 * t, 0.2, 0.3]',
    }


def test_Scenario_aliasing_1(assembly, caplog):
    """Same as test 0, with additional connections.
    """
    head = assembly
    head.connect(head.foo1.x_out, head.foo2.x_in)
    head.connect(head.foo2.x_out, head.bar1.a_in, dict(zip('xyz', 'abc')))
    driver = head.add_driver(EulerExplicit('driver'))

    scenario = Scenario('scenario', driver)

    with caplog.at_level(logging.INFO):
        scenario.add_init({
            'foo1.x_in.z': 1.3,
            'x_in.x': 'x_in.z + 1',
            'bar2.x': 0.1,  # pulled as `alpha`
        })
        scenario.add_values({
            'foo1.x_in.y': '2 * cos(t)',
            'bar1.v[::2]': '[0.1 * t, 0.2, 0.3]',  # pulled as `theta`
        })
    assert len(caplog.records) == 4
    assert re.match(
        "Replace 'foo1.x_in.z' by 'x_in.z'",
        caplog.records[0].message
    )
    assert re.match(
        "Replace 'bar2.x' by 'alpha'",
        caplog.records[1].message
    )
    assert re.match(
        "Replace 'foo1.x_in.y' by 'x_in.y'",
        caplog.records[2].message
    )
    assert re.match(
        "Replace 'bar1.v' by 'theta'",
        caplog.records[3].message
    )
    # Add connected inputs to scenario
    with pytest.warns(UserWarning, match="Skip connected variable 'bar1.a_in.a'"):
        scenario.add_init({
            'bar1.a_in.a': 0.5,  # connected
            'bar1.a_in.d': 2.5,  # not connected
        })
    with pytest.warns(UserWarning, match="Skip connected variable 'bar1.a_in.b'"):
        scenario.add_values({
            'bar1.a_in.b': 'sin(t)',
        })
    with pytest.warns(UserWarning, match="Skip connected variable 'foo2.x_in.x'"):
        scenario.add_values({
            'foo2.x_in.x': Interpolator(data=[(0, 0), (5, -2), (1000, 500)]),
        })
    
    init_conds = map(str, scenario.init_values)
    time_conds = map(str, scenario.case_values)

    assert set(init_conds) == {
        'x_in.z = 1.3',
        'x_in.x = x_in.z + 1',
        'alpha = 0.1',
        'bar1.a_in.d = 2.5',
    }
    assert set(time_conds) == {
        'x_in.y = 2 * cos(t)',
        'theta[::2] = [0.1 * t, 0.2, 0.3]',
    }


def test_Scenario_aliasing_2(assembly, caplog):
    """Same as test 0, using `ExplicitTimeDriver.set_scenario`
    instead of `Scenario.set_init` and `set_values`.
    """
    head = assembly
    driver = head.add_driver(EulerExplicit('driver'))
    with caplog.at_level(logging.INFO):
        driver.set_scenario(
            init = {
                'foo1.x_in.z': 1.3,
                'x_in.x': 'x_in.z + 1',
                'bar2.x': 0.1,  # pulled as `alpha`
            },
            values = {
                'foo1.x_in.y': '2 * cos(t)',
                'foo2.x_in.x': 'exp(-t / 4) * foo1.x_in.y',
                'bar1.v[::2]': '[0.1 * t, 0.2, 0.3]',  # pulled as `theta`
            }
        )
    assert set(record.message for record in caplog.records) == {
        "Replace 'foo1.x_in.y' by 'x_in.y' in time scenario.",
        "Replace 'foo1.x_in.z' by 'x_in.z' in time scenario.",
        "Replace 'bar1.v' by 'theta' in time scenario.",
        "Replace 'bar2.x' by 'alpha' in time scenario.",
    }
    scenario: Scenario = driver.scenario  # tested object
    
    init_conds = map(str, scenario.init_values)
    time_conds = map(str, scenario.case_values)

    assert set(init_conds) == {
        'x_in.z = 1.3',
        'x_in.x = x_in.z + 1',
        'alpha = 0.1',
    }
    assert set(time_conds) == {
        'x_in.y = 2 * cos(t)',
        'foo2.x_in.x = exp(-t / 4) * foo1.x_in.y',
        'theta[::2] = [0.1 * t, 0.2, 0.3]',
    }


def test_Scenario_aliasing_3(assembly, clock):
    """Check out-of-context warning.
    """
    head = assembly
    # Add time driver to sub-system `head.bar2`:
    driver = head.bar2.add_driver(EulerExplicit('driver'))
    scenario = Scenario('scenario', driver)

    pattern = "Variable 'x' is aliased by 'head.alpha', defined outside the context of 'bar2'"

    with pytest.warns(UserWarning, match=pattern):
        scenario.add_init({
            'x': 0.1,  # pulled as `alpha`
        })
    with pytest.warns(UserWarning, match=pattern):
        scenario.add_values({
            'x': 'cos(t)',  # pulled as `alpha`
        })
    
    init_conds = map(str, scenario.init_values)
    time_conds = map(str, scenario.case_values)

    assert set(init_conds) == {'x = 0.1'}
    assert set(time_conds) == {'x = cos(t)'}
    assert scenario.init_values[0].eval_context is head.bar2
    assert scenario.case_values[0].eval_context is head.bar2

    head.alpha = 0.0
    head.bar2.x = -0.5
    scenario.apply_init_values()
    assert head.alpha == 0
    assert head.bar2.x == 0.1

    clock.time = 1
    scenario.update_values()
    assert head.alpha == 0
    assert head.bar2.x == pytest.approx(np.cos(1))
