from bisect import bisect_left
from dataclasses import dataclass
from math import pi
from typing import Optional, Iterable

import numpy as np

from .PeriodicSwitch import PeriodicSwitch


@dataclass(eq=False)
class SwitchPWM(PeriodicSwitch):
    """
    A periodic, multi-level PWM modulation source.

    You can supply this source a constant pattern that is repeated throughout a simulation.

    Changing patterns on the same source object is currently not possible. Please instantiate another object with
    the new pattern.
    """
    def __init__(self, pattern_timings: Iterable[float], initial_state: bool = False, *args, **kwargs):
        r"""
        :param pattern_timings:
            The timings between each amplitude change in `pattern_levels` in rad. The range for pattern timings lies
            inside :math:`(0, 2\pi)`. Timings outside this range will be ignored.
        :param initial_state:
            Whether the first state until the next specified pattern timing will be on (`True`) or off (`False`).
        """
        super().__init__(*args, **kwargs)

        self._pattern_timings = list(pattern_timings)
        self._initial_state = initial_state

    def __repr__(self):
        signal_pattern = ''.join(
            '\u2588' if self.get_switch_signal(phase) else '\u2581'
            for phase in np.linspace(0, 2 * pi, 50))

        return f'{type(self).__name__}(pattern: {signal_pattern})'

    def get_switch_signal(self, phase: float) -> bool:
        even = bisect_left(self._pattern_timings, phase) % 2 == 0
        return (even and self._initial_state) or not (even or self._initial_state)

    def next_switch_event(self, phase1: float, phase2: float) -> Optional[float]:
        if phase1 == 0.0 and len(self._pattern_timings) % 2 == 1:
            return 0.0

        a = bisect_left(self._pattern_timings, phase1)
        b = bisect_left(self._pattern_timings, phase2, a)

        if a == b:
            return None

        return self._pattern_timings[a]
