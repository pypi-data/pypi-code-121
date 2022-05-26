import numpy as np

from cosapp.utils import distributions
from cosapp.ports import Port


class XPort(Port):
    def setup(self):
        self.add_variable("x")


class X2Port(Port):
    def setup(self):
        self.add_variable("x1")
        self.add_variable("x2")


class X3Port(Port):
    def setup(self):
        self.add_variable("x1")
        self.add_variable("x2")
        self.add_variable("x3")


class V1dPort(Port):
    def setup(self):
        self.add_variable("x", np.r_[1., 2., 3.])


class V2dPort(Port):
    def setup(self):
        self.add_variable(
            "x", np.r_[11., 12., 13., 21., 22., 23., 31., 32., 33.].reshape((3, 3))
        )


class TimePort(Port):
    def setup(self):
        self.add_variable("time_", 0., unit="s")
        self.add_variable("deltaTime", 0., unit="s")


class NumPort(Port):
    def setup(self):
        self.add_variable("Pt", 101325., unit="Pa")
        self.add_variable("W", 1., unit="kg/s")


class MechPort(Port):
    def setup(self):
        self.add_variable("XN", 100., unit="rpm")
        self.add_variable("PW", 0., unit="W")


class FluidState(Port):
    def setup(self):
        self.add_variable("Tt", 273.15, unit="K")
        self.add_variable("Pt", 101325., unit="Pa")


class FlowPort(Port):
    def setup(self):
        self.add_variable("W", unit="kg/s")


class FluidPort(Port):
    def setup(self):
        self.add_variable("Tt", 273.15, unit="K")
        self.add_variable("Pt", 101325., unit="Pa")
        self.add_variable("W", 0., unit="kg/s")

    def wr(self):
        return self.W * (self.Tt / 288.15) ** 0.5 / (self.Pt / 101325.)


class XPortPerturbed(Port):
    def setup(self):
        self.add_variable('x', 1., distribution=distributions.Uniform(best=-0.1, worst=0.2), valid_range=(0., 3.))
