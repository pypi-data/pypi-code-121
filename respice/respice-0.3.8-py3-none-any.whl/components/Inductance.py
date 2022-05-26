from dataclasses import dataclass, field

import numpy as np

from .TwoTerminalCurrentComponent import TwoTerminalCurrentComponent


@dataclass(eq=False)
class Inductance(TwoTerminalCurrentComponent):
    """
    Describes an ideal inductance (L*dI/dt = V)

    value:
        The inductance value in Henry.
    state_current:
        The momentary current. This is a state variable updated consecutively
        on each simulation iteration. However, you might set it ahead simulation
        to describe the inductance's initial state.
    state_voltage:
        The momentary voltage. Since this component uses the midpoint-method for
        calculation, this additional state variable is introduced for better accuracy.
        This is a state variable updated consecutively on each simulation iteration.
        However, you might set it ahead simulation to describe the inductance's initial state.
    """
    value: float

    state_current: float = field(default=0.0, repr=False)
    state_voltage: float = field(default=0.0, repr=False)

    def get_current(self, v: float, t1: float, t2: float) -> float:
        return self.state_current + (self.state_voltage + v) / (2 * self.value) * (t2 - t1)

    def get_jacobian(self, v: float, t1: float, t2: float) -> float:
        return (t2 - t1) / (2 * self.value)

    def update(self, v_i: np.ndarray, t1: float, t2: float):
        v = v_i[0]
        self.state_current = self.get_current(v, t1, t2)
        self.state_voltage = v

    @property
    def state(self):
        return self.state_current, self.state_voltage

    @state.setter
    def state(self, val):
        self.state_current, self.state_voltage = val


L = Inductance
