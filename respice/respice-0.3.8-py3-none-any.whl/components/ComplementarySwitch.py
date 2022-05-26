from dataclasses import dataclass
from typing import Optional, Callable

import numpy as np

from .Switch import Switch


@dataclass(eq=False)
class ComplementarySwitch(Switch):
    """
    A convenience class that acts complementary to another specified switch.

    switch:
        The switch to generate the complementary signal for.
    """
    switch: Switch

    def switch_state(self, t: float) -> bool:
        return not self.switch.switch_state(t)

    def next_event(self, vi: Callable[[float], np.ndarray], t1: float, t2: float) -> Optional[float]:
        return self.switch.next_event(vi, t1, t2)
