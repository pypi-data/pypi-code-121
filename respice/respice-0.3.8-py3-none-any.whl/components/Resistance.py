from dataclasses import dataclass

from .TwoTerminalCurrentComponent import TwoTerminalCurrentComponent


@dataclass(eq=False)
class Resistance(TwoTerminalCurrentComponent):
    """
    Describes an ideal resistance (R*I = V).

    value:
        The resistance value in Ohm.
    """
    value: float

    def get_current(self, v: float, t1: float, t2: float) -> float:
        return v / self.value

    def get_jacobian(self, v: float, t1: float, t2: float) -> float:
        return 1 / self.value


R = Resistance
