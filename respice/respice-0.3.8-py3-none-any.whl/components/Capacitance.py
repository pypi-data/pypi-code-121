from dataclasses import dataclass, field

import numpy as np

from .TwoTerminalVoltageComponent import TwoTerminalVoltageComponent


@dataclass(eq=False)
class Capacitance(TwoTerminalVoltageComponent):
    """
    Represents an ideal capacitance.

    value:
        The capacitance value (measured in Farad).
    state_voltage:
        The momentary voltage. This is a state variable updated consecutively
        on each simulation iteration. However, you might set it ahead simulation
        to describe the capacitance's initial state.
    state_current:
        The momentary current. Since this component uses the midpoint-method for
        calculation, this additional state variable is introduced for better accuracy.
        This is a state variable updated consecutively on each simulation iteration.
        However, you might set it ahead simulation to describe the capacitance's initial state.
    """
    value: float

    state_voltage: float = field(default=0.0, repr=False)
    state_current: float = field(default=0.0, repr=False)

    def get_voltage(self, i: float, t1: float, t2: float) -> float:
        return self.state_voltage + (self.state_current + i) / (2 * self.value) * (t2 - t1)

    def get_jacobian(self, i: float, t1: float, t2: float) -> float:
        return (t2 - t1) / (2 * self.value)

    def update(self, v_i: np.ndarray, t1: float, t2: float):
        i = v_i[0]
        self.state_voltage = self.get_voltage(i, t1, t2)
        self.state_current = i

    @property
    def state(self):
        return self.state_voltage, self.state_current

    @state.setter
    def state(self, val):
        self.state_voltage, self.state_current = val


C = Capacitance
