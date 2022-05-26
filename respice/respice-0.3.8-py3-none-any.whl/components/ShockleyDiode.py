from dataclasses import dataclass
from math import exp

from .TwoTerminalCurrentComponent import TwoTerminalCurrentComponent


@dataclass(eq=False)
class ShockleyDiode(TwoTerminalCurrentComponent):
    """
    Describes an ideal Schockley Diode backed by the ideal Schockley equation.

    See https://en.wikipedia.org/wiki/Diode_modelling#Shockley_diode_model

    For a simpler, linearized model with better solution convergence properties,
    see `respice.components.LinearizedShockleyDiode`.

    i_s:
        Reverse bias saturation current (also known as leakage current).
        Depending on the material used, common values are
        * silicon diodes: usually between 10^-12 A and 10^-10 A (1uA to 100uA).
        * germanium diodes: about 10^-4 A (0.1mA)
    v_t:
        Thermal voltage V_T. For approximate room temperate 300K this value
        is 25.85mV (0.02585V). This is default.
    n:
        Ideality factor (also known as quality factor). By default 1.
    """
    i_s: float = 1e-12
    v_t: float = 0.02585
    n: float = 1.0

    def get_current(self, v: float, t1: float, t2: float) -> float:
        return self.i_s * (exp(v / (self.n * self.v_t)) - 1)

    def get_jacobian(self, v: float, t1: float, t2: float) -> float:
        return self.i_s / (self.n * self.v_t) * exp(v / (self.n * self.v_t))
