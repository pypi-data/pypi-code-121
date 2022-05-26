from dataclasses import dataclass
from math import pi
from typing import Optional

from .PeriodicSwitch import PeriodicSwitch


@dataclass(eq=False)
class SwitchRectangular(PeriodicSwitch):
    """
    A switch that switches on and off according to a rectangular-signal pattern.

    duty:
        The duty cycle. Meaningful values lie between 0 and 1.
    """
    duty: float = 0.5

    def get_switch_signal(self, phase: float) -> bool:
        return phase < 2 * pi * self.duty

    def next_switch_event(self, phase1: float, phase2: float) -> Optional[float]:
        if phase1 == 0.0:
            return 0.0

        dutyphase = self.duty * 2 * pi
        if phase1 <= dutyphase <= phase2:
            return dutyphase

        return None
