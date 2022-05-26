from typing import Union
import numpy as np
from cosapp.systems import System
from cosapp.tests.library.ports import V1dPort, V2dPort


class Strait1dLine(System):
    def setup(self, **kwargs):
        self.add_input(V1dPort, "in_")
        self.add_inward("a", np.ones(3))
        self.add_inward("b", np.zeros(3))
        self.add_output(V1dPort, "out")

    def compute(self):
        self.out.x = self.a * self.in_.x + self.b


class Strait2dLine(System):
    def setup(self, **kwargs):
        self.add_input(V2dPort, "in_")
        self.add_inward("a", np.ones(3, 3))
        self.add_inward("b", np.zeros(3, 3))
        self.add_output(V2dPort, "out")

    def compute(self):
        self.out.x = self.a * self.in_.x + self.b


class Splitter1d(System):
    def setup(self, **kwargs):
        self.add_input(V1dPort, "in_")
        self.add_inward("s", 0.1 * np.ones(3))
        self.add_output(V1dPort, "out1")
        self.add_output(V1dPort, "out2")

    def compute(self):
        self.out1.x = self.s * self.in_.x
        self.out2.x = (1. - self.s) * self.in_.x


class Merger1d(System):
    def setup(self, **kwargs):
        self.add_input(V1dPort, "in1")
        self.add_input(V1dPort, "in2")
        self.add_output(V1dPort, "out")

    def compute(self):
        self.out.x = self.in1.x + self.in2.x


class AllTypesSystem(System):
    def setup(self, **kwargs):
        dim = 3
        self.add_property("dimension", dim)
        self.add_input(V1dPort, "in_")
        self.add_inward("a", np.ones(dim), unit="kg")
        self.add_inward("b", np.zeros(dim), unit="N")
        self.add_inward("c", 23, unit="m")
        self.add_inward("e", "sammy")
        self.add_outward("d", list())
        self.add_output(V1dPort, "out")

    def compute(self):
        self.out.x = self.a * self.in_.x + self.b
        self.d = [self.c, self.e]


class BooleanSystem(System):
    def setup(self, **kwargs):
        self.add_input(V1dPort, "in_")
        self.add_inward("a", True)

