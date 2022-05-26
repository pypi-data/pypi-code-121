from dataclasses import dataclass

from .TwoTerminalVoltageComponent import TwoTerminalVoltageComponent


@dataclass(eq=False)
class VoltageSourceDC(TwoTerminalVoltageComponent):
    """
    A DC voltage supply.

    Voltage is in the same direction as the branch points in the circuit graph.

    value:
        The voltage emitted by this supply (measured in Volt).
    """
    value: float

    def get_voltage(self, i: float, t1: float, t2: float) -> float:
        return self.value

    def get_jacobian(self, i: float, t1: float, t2: float) -> float:
        return 0
