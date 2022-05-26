import abc

from cosapp.systems import System
from cosapp.tests.library.ports import NumPort, TimePort


# =============================================================#
# PressureLoss
#   input
#       flnum_in
#   output
#       flnum_out
#   equation
#       Pt_out = Pt_in - K * Q_in**2
#       Q_out = Q_in
#   Family
#   Sys
#   0D
#
class PressureLossFamily(abc.ABC):
    def __init__(self):
        pass


class FalseSystem:
    pass


class PressureLoss0D(System, PressureLossFamily):

    def setup(self):
        self.add_input(NumPort, "flnum_in")
        self.add_inward("K", 100.)
        self.add_outward("delta_p", 0.)
        self.add_output(NumPort, "flnum_out")

    def compute(self):
        self.flnum_out.W = self.flnum_in.W
        self.flnum_out.Pt = self.flnum_in.Pt - self.K * self.flnum_in.W ** 2
        self.delta_p = self.flnum_out.Pt - self.flnum_in.Pt


class PressureLossSys(System, PressureLossFamily):

    def setup(self):
        self.add_input(NumPort, "flnum_in")
        self.add_inward("K11", 100.)
        self.add_outward("delta_p12", 0.)
        self.add_output(NumPort, "flnum_out")

    def toPressureLoss0D(self):
        Pt_out = self.flnum_out.Pt
        Pt_in = self.flnum_in.Pt
        W_out = self.flnum_out.W
        W_in = self.flnum_in.W

        self.K = (Pt_in - Pt_out) / (W_in + W_out) ** 2 * 4


# =============================================================#
# Tank
#   description
#       the flow out from the tank is limited to W_out_tank execpt when the tank is full
#   input
#       flnum_in
#   output
#       flnum_out
#   equation
#       Pt_out = Pt_in
#       if (vol <= 0.)                      the tank is umpty
#           W_out = min(W_in, W_out_tank)
#       if (vol > 0. and vol < volMax)      the tank absorb the flow
#           W_out = W_out_tank
#       if (vol >= volMax)                  the tank is full
#           W_out = max(W_in, W_out_tank)
#   Family      To be done
#   Sys         To be done
#   0D          To be done
#
class Tank(System):

    def setup(self):
        self.add_input(NumPort, "flnum_in")
        self.add_inward("volMax", 100.)
        self.add_inward("vol", 0.)
        self.add_inward("W_out_tank", 1.)
        self.add_input(TimePort, "time_", {"time_": 0., "deltaTime": 0.})
        self.add_output(NumPort, "flnum_out")

    def compute(self):
        self.flnum_out.Pt = self.flnum_in.Pt

        W_in = self.flnum_in.W
        W_out = self.flnum_out.W

        volMax = self.volMax

        vol = self.vol
        W_out_tank = self.W_out_tank

        deltaTime = self.time_.deltaTime
        time = self.time_.time_

        if vol <= 0.:
            W_out = min(W_in, W_out_tank)

        if 0. < vol < volMax:
            W_out = W_out_tank
            deltaTimeMax = min(vol / W_out, (volMax - vol)) / W_out

        if vol >= volMax:
            W_out = max(W_in, W_out_tank)

        if deltaTime != 0:
            vol = vol - deltaTime * (W_out - W_in)

        self.flnum_out.W = W_out
        self.vol = vol


# =============================================================#
# Tank
#   description
#       the flow out from the tank is limited to W_out_tank execpt when the tank is full
#   extension to be done
#       Family, 0D, smooth in time
#   input
#       flnum_in
#   output
#       flnum_out
#   equation
#       Pt_out = Pt_in
#       if (vol <= 0.)                      the tank is umpty
#           W_out = min(W_in, W_out_tank)
#       if (vol > 0. and vol < volMax)      the tank absorb the flow
#           W_out = W_out_tank
#       if (vol >= volMax)                  the tank is full
#           W_out = max(W_in, W_out_tank)
#   Family      To be done
#   Sys         To be done
#   0D          To be done
#
class Splitter12(System):

    def setup(self):
        self.add_input(NumPort, "flnum_in")
        self.add_output(NumPort, "flnum_out1")
        self.add_output(NumPort, "flnum_out2")
        self.add_inward("x", 0.8)

        self.add_unknown("x")

    def compute(self):
        self.flnum_out1.W = self.flnum_in.W * self.x
        self.flnum_out2.W = self.flnum_in.W * (1 - self.x)
        self.flnum_out1.Pt = self.flnum_in.Pt
        self.flnum_out2.Pt = self.flnum_in.Pt


class Mixer21(System):

    def setup(self):
        self.add_input(NumPort, "flnum_in1")
        self.add_input(NumPort, "flnum_in2")
        self.add_output(NumPort, "flnum_out")
        self.add_outward("epsilon")

        self.add_equation("epsilon == 0")

    def compute(self):
        W1 = self.flnum_in1.W
        W2 = self.flnum_in2.W
        W = W1 + W2
        self.flnum_out.W = W

        Pt1 = self.flnum_in1.Pt
        Pt2 = self.flnum_in2.Pt
        Pt = (W1 * Pt1 + W2 * Pt2) / (W1 + W2)
        self.flnum_out.Pt = Pt

        self.epsilon = (Pt2 - Pt1) / (Pt2 + Pt1)
