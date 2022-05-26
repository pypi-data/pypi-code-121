from dataclasses import dataclass

from .TwoTerminalCurrentComponent import TwoTerminalCurrentComponent


@dataclass(eq=False)
class CurrentSourceDC(TwoTerminalCurrentComponent):
    """
    A DC current supply.

    Current emits in the same direction as the edge points in the circuit graph.

    value:
        The current emitted by this supply (measured in Amperes).
    """
    value: float

    def get_current(self, v: float, t1: float, t2: float) -> float:
        return self.value

    def get_jacobian(self, v: float, t1: float, t2: float) -> float:
        return 0.0
