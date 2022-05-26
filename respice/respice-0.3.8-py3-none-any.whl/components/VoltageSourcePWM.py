from bisect import bisect_left
from math import pi
from types import SimpleNamespace
from typing import Optional, Iterable

import numpy as np

from .PeriodicVoltageSource import PeriodicVoltageSource


class VoltageSourcePWM(PeriodicVoltageSource):
    """
    A periodic, multi-level PWM modulation source.

    You can supply this source a constant pattern that is repeated throughout a simulation.

    Changing patterns on the same source object is currently not possible. Please instantiate another object with
    the new pattern.
    """
    def __init__(self, pattern_levels: Iterable[float], pattern_timings: Iterable[float], *args, **kwargs):
        r"""
        :param pattern_levels:
            The amplitude values of the pattern.
        :param pattern_timings:
            The timings between each amplitude change in `pattern_levels` in rad. The range for pattern timings lies
            inside :math:`(0, 2\pi)`. Timings outside this range will be ignored.
            Note that the length of this iterable must be always one less than `len(pattern_levels)`.
            This parameter *must* be sorted beforehand!
        """
        super().__init__(*args, **kwargs)

        self._pattern_timings = list(pattern_timings)
        self._pattern_levels = list(pattern_levels)

        assert len(self._pattern_timings) + 1 == len(self._pattern_levels)

        self._cache = SimpleNamespace()
        self._cache.repr_pattern = None

    def __repr__(self):
        if self._cache.repr_pattern is None:
            # Generate human readable pattern for repr().
            pattern_length = 50
            minv = min(self._pattern_levels)
            maxv = max(self._pattern_levels)
            chardict = {
                0: '\u2581',
                1: '\u2582',
                2: '\u2583',
                3: '\u2584',
                4: '\u2585',
                5: '\u2586',
                6: '\u2587',
                7: '\u2588',
                8: '\u2588',
            }

            self._cache.repr_pattern = ''.join(
                chardict[int((self.get_signal(phase) - minv) / (maxv - minv) * (len(chardict) - 1))]
                for phase in np.linspace(0, 2 * pi, pattern_length))

        return f'{type(self).__name__}(pattern: {self._cache.repr_pattern})'

    def get_signal(self, phase: float) -> float:
        return self._pattern_levels[bisect_left(self._pattern_timings, phase)]

    def next_signal_event(self, phase1: float, phase2: float) -> Optional[float]:
        if phase1 == 0.0 and self._pattern_levels[0] != self._pattern_levels[-1]:
            return 0.0

        a = bisect_left(self._pattern_timings, phase1)
        b = bisect_left(self._pattern_timings, phase2, a)

        if a == b:
            return None

        return self._pattern_timings[a]
