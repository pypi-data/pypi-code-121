from cosapp.utils.distributions import Uniform
from cosapp.systems import SystemFamily, System
from cosapp.tests.library.ports import XPort, X2Port, X3Port
import numpy as np


class MultiplyFamily(SystemFamily):

    def __init__(self, name: str):
        super(MultiplyFamily, self).__init__(name)

        self.family_name = 'Multiply'

        self.modelings.add('Multiply1', fidelity=0.99, cost=0.1)
        self.modelings.add('Multiply2', fidelity=1, cost=0.3)
        self.modelings.add('Multiply3', fidelity=1.01, cost=0.9)


class Multiply1(MultiplyFamily):

    def setup(self):
        self.add_input(XPort, 'p_in', {'x': 1.})
        self.add_inward('K1', 5., distribution=Uniform(worst=-1, best=+1))
        self.add_output(XPort, 'p_out', {'x': 1.})

    def compute(self):
        self.p_out.x = self.p_in.x * self.K1

    def Multiply1_to_Multiply2(self):
        rtn = Multiply2(self.name)
        rtn.parent = self.parent

        rtn.K1 = self.K1 ** 0.5
        rtn.K2 = rtn.K1

        self.update_connections(rtn)
        return rtn

    def Multiply1_to_Multiply3(self):
        rtn = Multiply3(self.name)
        rtn.parent = self.parent

        rtn.K1 = self.K1 ** (1. / 3.)
        rtn.K2 = rtn.K1
        rtn.K3 = rtn.K1

        self.update_connections(rtn)
        return rtn


class Multiply2(MultiplyFamily):

    def setup(self):
        self.add_input(XPort, 'p_in', {'x': 1.})
        self.add_inward('K1', 5., distribution=Uniform(worst=-0.1, best=+0.1))
        self.add_inward('K2', 5., distribution=Uniform(worst=-0.2, best=+0.2))
        self.add_output(XPort, 'p_out', {'x': 1.})

        self.add_outward('Ksum', 0.)

    def compute(self):
        self.p_out.x = self.p_in.x * self.K1 * self.K2
        self.Ksum = self.K1 + self.K2

    def Multiply2_to_Multiply1(self):
        rtn = Multiply1(self.name)
        rtn.parent = self.parent

        rtn.K1 = self.K1 * self.K2

        self.update_connections(rtn)
        return rtn

    def Multiply2_to_Multiply3(self):
        rtn = Multiply3(self.name)
        rtn.parent = self.parent

        rtn.K1 = (self.K1 * self.K2) ** (1 / 3)
        rtn.K2 = rtn.K1
        rtn.K3 = rtn.K1

        self.update_connections(rtn)
        return rtn


class Multiply2Derivative(MultiplyFamily):

    def setup(self):
        self.add_input(XPort, 'p_in', {'x': 1.})
        self.add_inward('K1', 5.)
        self.add_inward('K2', 5.)
        self.add_output(XPort, 'p_out', {'x': 1.})

        self.add_inward('dK1_dK2', 0.)
        self.add_derivative('inwards.dK1_dK2', 'inwards.K1', 'inwards.K2')

    def compute(self):
        self.p_out.x = self.p_in.x * self.K1 * self.K2


class Multiply3(MultiplyFamily):

    def setup(self):
        self.add_input(XPort, 'p_in', {'x': 1.})
        self.add_inward({'K1': 5., 'K2': 5., 'K3': 5.})
        self.add_output(XPort, 'p_out', {'x': 1.})

    def compute(self):
        self.p_out.x = self.p_in.x * self.K1 * self.K2 * self.K3

    def Multiply3_to_Multiply1(self):
        rtn = Multiply1(self.name)
        rtn.parent = self.parent

        rtn.K1 = self.K1 * self.K2 * self.K3

        self.update_connections(rtn)
        return rtn

    def Multiply3_to_Multiply2(self):
        rtn = Multiply2(self.name)
        rtn.parent = self.parent

        rtn.K1 = (self.K1 * self.K2 * self.K3) ** 0.5
        rtn.K2 = rtn.K1

        self.update_connections(rtn)
        return rtn


class Multiply4(System):

    def setup(self):
        self.add_input(XPort, 'p_in', {'x': 1.})
        self.add_inward('K1', 2., valid_range=(1., 6.))
        self.add_inward('K2', 1., distribution=Uniform(worst=-0.1, best=0.1))
        self.add_output(XPort, 'p_out', {'x': 1.})

    def compute(self):
        self.p_out.x = self.p_in.x * self.K1 * self.K2


class MultiplySystem(System):
    def setup(self):
        self.add_input(XPort, 'p_in', {'x': 1.})
        self.add_output(XPort, 'p_out', {'x': 1.})

        self.add_child(Multiply1('mult1'))
        self.connect(self.p_in, self.mult1.p_in)
        self.connect(self.p_out, self.mult1.p_out)

        self.exec_order = ['mult1']


class MultiplySystem2(System):
    def setup(self):
        self.add_child(Multiply1('mult1'))
        self.add_child(Multiply1('mult2'))

        self.connect(self.mult1.p_out, self.mult2.p_in)

        self.exec_order = ['mult1', 'mult2']


class MultiplyVector2(System):
    def setup(self):
        self.add_input(X2Port, 'p_in', {'x1': 1., 'x2': 1.})
        self.add_inward('k1', 5.)
        self.add_inward('k2', 5.)
        self.add_output(XPort, 'p_out', {'x': 1.})

    def compute(self):
        self.p_out.x = self.k1 * self.p_in.x1 + self.k2 * self.p_in.x2


class MultiplyVector3(System):

    def setup(self):
        self.add_input(X3Port, 'p_in', {'x1': 1., 'x2': 1., 'x3': 1.})
        self.add_inward('k1', 5.)
        self.add_inward('k2', 5.)
        self.add_inward('k3', 5.)
        self.add_output(XPort, 'p_out', {'x': 1.})

    def compute(self):
        self.p_out.x = self.k1 * self.p_in.x1 + self.k2 * self.p_in.x2 + self.k3 * self.p_in.x3


class ExponentialLoad(System):
    """ExponentialLoad expression

    $load = \\exp(a * (p_in.x - b)) + c$

    Default values (a, b, c) = (1, 0, 0) => load = exp(p_in.x)
    """

    def setup(self, **kwargs):
        self.add_input(XPort, 'p_in')
        self.add_inward('a', 1)
        self.add_inward('b', 0)
        self.add_inward('c', 0)
        self.add_outward('load_', 0.)
        self.add_output(XPort, 'p_out')

    def compute(self):
        self.load_ = np.exp(self.a * (self.p_in.x - self.b)) + self.c
        self.p_out.x = self.p_in.x


class NonLinear1(System):

    def setup(self):
        self.add_input(XPort, 'p_in', {'x': 1.})
        self.add_inward('k1', 5.)
        self.add_inward('k2', 5.)
        self.add_output(XPort, 'p_out', {'x': 1.})

    def compute(self):
        self.p_out.x = self.k1 * self.p_in.x ** self.k2


class NonLinear3(System):

    def setup(self):
        self.add_input(X3Port, 'p_in', {'x1': 1., 'x2': 1., 'x3': 1.})
        self.add_inward('k1', 5.)
        self.add_inward('k2', 5.)
        self.add_inward('k3', 5.)
        self.add_output(XPort, 'p_out', {'x': 1.})

    def compute(self):
        self.p_out.x = self.k1 * self.p_in.x1 ** 2 + self.k2 / self.p_in.x2 ** 0.5 + self.k3 * self.p_in.x3


class Merger(System):

    def setup(self):
        self.add_input(XPort, 'p1_in', {'x': 1.})
        self.add_input(XPort, 'p2_in', {'x': 1.})
        self.add_output(XPort, 'p_out', {'x': 1.})

    def compute(self):
        self.p_out.x = self.p1_in.x + self.p2_in.x


class Splitter(System):

    def setup(self):
        self.add_input(XPort, 'p_in', {'x': 1.})
        self.add_inward('split_ratio', 0.1)
        self.add_output(XPort, 'p1_out', {'x': 1.})
        self.add_output(XPort, 'p2_out', {'x': 1.})

    def compute(self):
        self.p1_out.x = self.p_in.x * self.split_ratio
        self.p2_out.x = self.p_in.x * (1 - self.split_ratio)


class IterativeNonLinear(System):

    def setup(self):
        self.add_child(NonLinear1('nonlinear'))
        self.add_child(Multiply2('mult2'))
        self.add_child(Merger('merger'))
        self.add_child(Splitter('splitter'))

        self.add_input(XPort, 'p_in', {'x': 1.})
        self.add_output(XPort, 'p_out', {'x': 1.})

        self.connect(self.p_in, self.merger.p1_in)
        self.connect(self.nonlinear.p_out, self.merger.p2_in)
        self.connect(self.merger.p_out, self.mult2.p_in)
        self.connect(self.mult2.p_out, self.splitter.p_in)
        self.connect(self.splitter.p1_out, self.nonlinear.p_in)
        self.connect(self.splitter.p2_out, self.p_out)

        self.exec_order = ['merger', 'mult2', 'splitter', 'nonlinear']


class IterativeNonLinearDerivative(System):

    def setup(self):
        self.add_child(NonLinear1('nonlinear'))
        self.add_child(Multiply2Derivative('mult2'))
        self.add_child(Merger('merger'))
        self.add_child(Splitter('splitter'))

        self.add_input(XPort, 'p_in', {'x': 1.})
        self.add_output(XPort, 'p_out', {'x': 1.})

        self.connect(self.p_in, self.merger.p1_in)
        self.connect(self.nonlinear.p_out, self.merger.p2_in)
        self.connect(self.merger.p_out, self.mult2.p_in)
        self.connect(self.mult2.p_out, self.splitter.p_in)
        self.connect(self.splitter.p1_out, self.nonlinear.p_in)
        self.connect(self.splitter.p2_out, self.p_out)

        self.exec_order = ['merger', 'mult2', 'splitter', 'nonlinear']
