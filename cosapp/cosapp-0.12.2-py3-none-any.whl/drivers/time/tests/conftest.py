import pytest

import numpy as np
from numbers import Number
from typing import Callable
from cosapp.ports import Port
from cosapp.systems import System
from cosapp.core.time import UniversalClock


@pytest.fixture(scope='function')
def clock():
    yield UniversalClock()
    # teardown
    UniversalClock().reset()


@pytest.fixture
def set_master_system():
    """Ensure the System class variable master is properly restored"""
    System._System__master_set = True
    try:
        yield
    finally:
        System._System__master_set = False


def case_factory(system_cls, name, **kwargs):
    """Case factory used in test fixtures below"""
    def _test_objects(driver_cls, **options):
        system = system_cls(name, **kwargs)
        driver = system.add_driver(driver_cls(**options))
        return system, driver
    return _test_objects

# <codecell>

class ExpRampOde(System):
    """
    System representing function f(t) = a * (1 - exp(-t / tau)),
    through ODE: tau * f' + f = a
    """
    def setup(self):
        self.add_inward('a', 1.0)
        self.add_inward('tau', 1.0)

        self.add_outward('df_dt', 0.0)
        self.add_transient('f', der='df_dt', max_time_step='tau / 5')

    def compute(self):
        self.df_dt = (self.a - self.f) / self.tau

    def __call__(self, t) -> float:
        """Analytical solution at time t"""
        return self.a * (1 - np.exp(-t / self.tau))


@pytest.fixture(scope='function')
def ode_case_1():
    return case_factory(ExpRampOde, 'ode')

# <codecell>

class GaussianOde(System):
    """
    System representing function f(t) = a * exp(-0.5 * ((t - t0) / tau)^2)
    """
    def setup(self):
        self.add_inward('a', 1.0)
        self.add_inward('t0', 4.0)
        self.add_inward('tau', 5.0)
        self.add_inward('df_dt', 1.0)
        self.add_inward('max_step', 0.1)

        self.add_transient('f', der='df_dt',
            # max_time_step='min(0.01 * a / max(abs(df_dt), 1e-8), 0.2)',
            max_time_step='max_step * a / max(abs(df_dt), 1e-8)',
        )

    def make_case(self, driver_cls, **options):
        settings = options.copy()
        init = settings.pop('init', {})
        values = settings.pop('values', {})
        values['df_dt'] = self.df_dt_expr
        driver = self.add_driver(driver_cls(**settings))
        driver.set_scenario(values=values, init=init)
        return driver

    @property
    def df_dt_expr(self) -> str:
        """Expression of the derivative of f(t)"""
        return "-a * (t - t0) / tau**2 * exp(-0.5 * ((t - t0) / tau)**2)"

    def solution(self, t, init=(0, 0)) -> float:
        """Analytical solution at time t, with initial condition f(t0) = f0,
        where (t0, f0) is given by tuple `init`."""
        exact = lambda t: self.a * np.exp(-0.5 * ((t - self.t0) / self.tau)**2)
        t0, f0 = init
        return exact(t) - exact(t0) + f0


@pytest.fixture(scope='function')
def gaussian_ode():
    return GaussianOde('gaussian_ode')

# <codecell>

class ScalarOde(System):
    """System representing ODE df/dt = F(t)"""
    def setup(self):
        self.add_inward('df')
        self.add_transient('f', der='df')


class VectorOde(System):
    """System representing ODE dv/dt = V(t) in vectorial form"""
    def setup(self, size=3):
        self.add_inward('dv', np.zeros(max(size, 1)))
        self.add_transient('v', der='dv')


@pytest.fixture(scope='function')
def scalar_ode_case():
    return case_factory(ScalarOde, 'scalar_ode')

@pytest.fixture(scope='function')
def vector_ode_case():
    return case_factory(VectorOde, 'vector_ode')

# <codecell>

class FloatPort(Port):
    def setup(self):
        self.add_variable('value', 0.0)


class Tank(System):
    def setup(self, rho=1e3):
        self.add_inward('area', 1.0, desc='Cross-section area')
        self.add_inward('rho', abs(rho), desc='Fluid density')

        self.add_input(FloatPort, 'flowrate')
        self.add_output(FloatPort, 'p_bottom')

        self.add_transient('height', der='flowrate.value / area')

    def compute(self):
        g = 9.81
        self.p_bottom.value = self.rho * g * self.height


class Pipe(System):
    """Poiseuille flow in a cylindrical pipe"""
    def setup(self):
        self.add_inward('D', 0.1, desc="Diameter")
        self.add_inward('L', 2.0, desc="Length")
        self.add_inward('mu', 1e-3, desc="Fluid dynamic viscosity")

        self.add_input(FloatPort, 'p1')
        self.add_input(FloatPort, 'p2')

        self.add_output(FloatPort, 'Q1')
        self.add_output(FloatPort, 'Q2')

        self.add_outward('k', desc='Pressure loss coefficient')

    def compute(self):
        self.k = np.pi * self.D**4 / (256 * self.mu * self.L)
        self.Q1.value = self.k * (self.p2.value - self.p1.value)
        self.Q2.value = -self.Q1.value


class CoupledTanks(System):
    """System describing two tanks connected by a pipe (viscous limit)"""
    def setup(self, rho=1e3):
        self.add_child(Tank('tank1', rho=rho))
        self.add_child(Tank('tank2', rho=rho))
        self.add_child(Pipe('pipe'))

        self.connect(self.tank1.p_bottom, self.pipe.p1)
        self.connect(self.tank2.p_bottom, self.pipe.p2)
        self.connect(self.tank1.flowrate, self.pipe.Q1)
        self.connect(self.tank2.flowrate, self.pipe.Q2)


class CoupledTanksSolution:
    """Analytical solution of dynamic system CoupledTanks"""
    def __init__(self, system, init):
        K = 9.81 * system.tank1.rho * system.pipe.k
        a = system.tank1.area / system.tank2.area
        self.__area_ratio = a
        self.__tau = system.tank1.area / ((1 + a) * K)
        self.initial_heights = init

    @property
    def characteristic_time(self):
        return self.__tau

    def __call__(self, t):
        tau = self.__tau
        a = self.__area_ratio
        h1_0, h2_0 = self.initial_heights
        dh = (h1_0 - h2_0) * np.exp(-t / tau)
        h1 = (a * h1_0 + h2_0 + dh) / (1 + a)
        h2 = h1 - dh
        return (h1, h2)


@pytest.fixture(scope='function')
def two_tank_case():
    def _test_objects(driver_cls, rho=1e3, **kwargs):
        system = CoupledTanks('coupledTanks', rho=rho)
        driver = system.add_driver(driver_cls(**kwargs))
        return system, driver
    return _test_objects


@pytest.fixture(scope='function')
def two_tank_solution():
    def _test_objects(system, init):
        return CoupledTanksSolution(system, init)
    return _test_objects

# <codecell>

class PointMass(System):
    """Free fall of a point mass, with friction"""
    def setup(self):
        self.add_inward('mass', 1.2, desc='Mass')
        self.add_inward('k', 0.1, desc='Friction coefficient')
        self.add_inward('g', np.r_[0, 0, -9.81], desc='Uniform acceleration field')

        self.add_outward('a', np.zeros(3), desc='Acceleration')

        self.add_transient('v', der='a', desc='Velocity')
        self.add_transient('x', der='v', desc='Position', max_time_step='0.1 * norm(a)')
   
    def compute(self):
        self.a = self.g - (self.k / self.mass) * self.v


class PointMassSolution:
    """Analytical solution of dynamic system PointMass"""
    def __init__(self, system, v0, x0=np.zeros(3)):
        m = system.mass
        k = system.k
        g = np.array(system.g)
        if m <= 0:
            raise ValueError("Mass must be strictly positive")
        x0 = np.asarray(x0)
        v0 = np.asarray(v0)
        if k > 0:
            omega = k / m
            tau = 1 / omega
            A = g * tau
        else:
            omega, tau = 0, np.inf
            A = np.full_like(g, np.inf)
        B = v0 - A
        def x_solution(t):
            wt = omega * t
            if wt < 1e-7:  # asymptotic expansion, to avoid exp overflow
                x = x0 + v0 * t + (0.5 * t) * (g * t - wt * v0) * (1 - wt / 3 * (1 - 0.25 * wt))
            else:
                x = x0 + A * t + B * tau * (1 - np.exp(-wt))
            return x
        def v_solution(t):
            wt = omega * t
            if wt < 1e-7:  # asymptotic expansion, to avoid exp overflow
                v = v0 + (g * t - v0  * wt) * (1 - wt * (0.5 - wt / 6))
            else:
                v = A + B * np.exp(-wt)
            return v
        self.__f = {
            'x': x_solution,
            'v': v_solution,
            'a': lambda t: g - v_solution(t) * omega
        }
        self.__omega = omega

    @property
    def omega(self):
        return self.__omega

    def a(self, t) -> np.ndarray:
        return self.__f['a'](t)

    def v(self, t) -> np.ndarray:
        return self.__f['v'](t)

    def x(self, t) -> np.ndarray:
        return self.__f['x'](t)

    def get_function(self, key) -> Callable[[float], np.ndarray]:
        return self.__f[key]


@pytest.fixture(scope='function')
def point_mass_case():
    return case_factory(PointMass, 'point')


@pytest.fixture(scope='function')
def point_mass_solution():
    def _test_objects(system, v0, x0=np.zeros(3)):
        return PointMassSolution(system, v0, x0)
    return _test_objects

# <codecell>

class PositionPort(Port):
    def setup(self):
        self.add_variable("x", np.zeros(3), desc="Position")

class KinematicsPort(Port):
    def setup(self):
        self.add_variable("v", np.zeros(3), desc="Velocity")

class DynamicsPort(Port):
    def setup(self):
        self.add_variable("a", np.zeros(3), desc="Acceleration")

class PointDynamics(System):
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
    def setup(self):
        self.add_input(KinematicsPort, 'kinematics')
        self.add_inward("k", 0.1, desc="Friction coefficient")

        self.add_outward("force", np.zeros(3))

    def compute(self):
        self.force = -self.k * self.kinematics.v

class PointMassWithPorts(System):
    def setup(self):
        self.add_child(PointFriction('friction'), pulling=['k', 'kinematics'])
        self.add_child(PointDynamics('dynamics'), pulling={
            'mass': 'mass',
            'force': 'force',
            'acc_ext': 'g',
            'acc': 'a',
            })

        self.exec_order = ['friction', 'dynamics']

        self.add_input(PositionPort, 'position')

        self.connect(self.friction.outwards, self.dynamics.inwards, {"force": "force_ext"})

        self.g = np.r_[0, 0, -9.81]

        self.add_transient('kinematics.v', der='a')
        self.add_transient('position.x', der='kinematics.v', max_time_step='0.1 * norm(a)')


@pytest.fixture(scope='function')
def pointMassWithPorts_case():
    return case_factory(PointMassWithPorts, 'point')


class DevilCase(System):

    def setup(self):
        self.add_inward("x", np.zeros(3))
        self.add_inward("v", np.zeros(3))
        self.add_inward("a", np.zeros(3))

        self.add_inward("y", np.zeros(3))
        self.add_inward("w", np.zeros(3))

        self.add_inward("alpha", 0.0)
        self.add_inward("omega", 0.0)
        self.add_inward("zeta", 0.0)

        self.add_transient("x", der="v")
        self.add_transient("v", der="a")

        self.add_transient("y", der="w")
        self.add_transient("w", der="25. * a * zeta")

        self.add_transient("alpha", der="omega")
        self.add_transient("omega", der="zeta")

        self.add_transient("beta", der="42. * cos(zeta)")

# <codecell>

class SystemWithRate(System):
    def setup(self):
        self.add_inward('k', 2.0)
        self.add_inward('U')
        self.add_rate('dU_dt', source='U', initial_value='k')


@pytest.fixture(scope='function')
def rate_case_1():
    return case_factory(SystemWithRate, 'system')

# <codecell>

class DampedMassSpring(System):
    """Harmonic oscillator"""
    def setup(self):
        self.add_inward('mass', 0.25)
        self.add_inward('length', 0.5, desc='Unloaded spring length')
        self.add_inward('c', 0.0, desc='Friction coefficient')
        self.add_inward('K', 0.1, desc='Spring stiffness')
        self.add_inward('x', 0.0, desc='Linear position')

        self.add_outward('F', 0.0, desc='Force')
        self.add_outward('a', 0.0, desc='Linear acceleration')

        self.add_transient('v', der='a')
        self.add_transient('x', der='v', max_time_step='0.1 * sqrt(mass / K)')
        
    def compute(self):
        self.F = self.K * (self.length - self.x) - self.c * self.v
        self.a = self.F / self.mass


class HarmonicOscillatorSolution:
    def __init__(self, system, x0, v0=0):
        K = system.K
        c = system.c
        m = system.mass
        L = system.length
        x0 -= L
        w0 = np.sqrt(K / m)
        self.__damping = dc = 0.5 * c / np.sqrt(m * K)
        wd = w0 * dc
        if self.over_damped:
            ws = w0 * np.sqrt(dc**2 - 1)
            A, B = 0.5 * (v0 + (wd + ws) * x0) / ws, 0.5 * (v0 + (wd - ws) * x0) / ws
            x = lambda t: L + A * np.exp(-(wd - ws) * t) - B * np.exp(-(wd + ws) * t)
            v = lambda t: -A * (wd - ws) * np.exp(-(wd - ws) * t) - B * (wd + ws) * np.exp(-(wd + ws) * t)
        else:
            ws = w0 * np.sqrt(1 - dc**2)
            A, B = (v0 + wd * x0) / ws, x0
            x = lambda t: L + np.exp(-wd * t) * (A * np.sin(ws * t) + B * np.cos(ws * t))
            v = lambda t: np.exp(-wd * t) * (
                + ws * (B * np.cos(ws * t) - B * np.sin(ws * t))
                - wd * (A * np.sin(ws * t) + B * np.cos(ws * t))
            )
        self.__f = {
            'x': x,
            'v': v,
            'a': lambda t: (K * (L - x(t)) - c * v(t)) / m
        }
    
    def a(self, t) -> float:
        return self.__f['a'](t)

    def v(self, t) -> float:
        return self.__f['v'](t)

    def x(self, t) -> float:
        return self.__f['x'](t)

    @property
    def damping(self) -> float:
        """Damping coefficient"""
        return self.__damping
    
    @property
    def over_damped(self) -> bool:
        return self.__damping > 1

    def get_function(self, key) -> Callable[[float], float]:
        return self.__f[key]


@pytest.fixture(scope='function')
def oscillator_case():
    return case_factory(DampedMassSpring, 'system')


@pytest.fixture(scope='function')
def oscillator_solution():
    def _test_objects(system, x0, v0=0):
        return HarmonicOscillatorSolution(system, x0, v0)
    return _test_objects


class MultimodeScalarOde(System):
    def setup(self):
        self.add_child(ScalarOde('ode'), pulling=['f', 'df'])
        self.add_outward_modevar('snapped', False)
        self.add_event('snap')  # event defining mode var `snapped`

    def transition(self):
        if self.snap.present:
            self.snapped = True


@pytest.fixture(scope='function')
def multimode_scalar_ode_case():
    return case_factory(MultimodeScalarOde, 'system')
