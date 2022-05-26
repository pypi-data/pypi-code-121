import pytest

import numpy as np
from cosapp.ports import Port
from cosapp.systems import System

from cosapp.tests.library.systems.multiply import IterativeNonLinear


class Float(Port):
    def setup(self):
        self.add_variable('x', 1.)


class AllCausality(System):
    def setup(self):
        self.add_input(Float, "in_")
        self.add_inward("in_x", 22.)
        self.add_output(Float, "out")
        self.add_outward("out_y", 42.)

@pytest.fixture(scope='function')
def allcausality():
    return AllCausality('test')


class TestType(System):

    def setup(self):
        self.add_inward("a", True)
        self.add_inward("b", 22)
        self.add_inward("c", 2.54)
        self.add_inward("d", "string")
        self.add_inward("f", np.array(True))
        self.add_inward("g", np.array(22))
        self.add_inward("h", np.array(2.54))
        self.add_inward("i", np.array("string"))

        self.add_inward("k", np.array([0., 1, 2, ]))
        self.add_inward("l", dict(a=1, b=2))

@pytest.fixture(scope='function')
def testtype():
    return TestType('test')


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

    def __call__(self, t):
        """Analytical solution at time t"""
        return self.a * (1 - np.exp(-t / self.tau))

@pytest.fixture(scope='function')
def ode():
    return ExpRampOde('ode')


class VectorSyst(System):

    def setup(self):
        self.add_inward("vi", [1, 2, 3])
        self.add_inward("vr", [1., 2., 3.])

@pytest.fixture(scope='function')
def vector_syst():
    return VectorSyst("syst")


@pytest.fixture(scope='function')
def iterativenonlinear():
    snl = IterativeNonLinear('nl')
    snl.splitter.split_ratio = 0.1
    snl.mult2.K1 = 1
    snl.mult2.K2 = 1
    snl.nonlinear.k1 = 1
    snl.nonlinear.k2 = 0.5
    snl.p_in.x = 1.0

    return snl


class VectorProblem(System):

    def setup(self):
        self.add_inward("x")
        self.add_outward("y")

        self.add_inward("dummy_coef", np.array([1., 2.]))

        self.add_unknown("dummy_coef[0]").add_equation("dummy_coef[0] == 0.5 * (x + y)")

    def compute(self):
        self.y = self.dummy_coef[1] + self.x

@pytest.fixture(scope='function')
def vector_problem():
    return VectorProblem("problem")
