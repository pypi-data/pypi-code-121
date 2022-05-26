from dataclasses import dataclass
from math import pi
from typing import Optional, Callable

import numpy as np

from .Switch import Switch


@dataclass(eq=False)
class PeriodicSwitch(Switch):
    """
    A switch with a periodic on/off-pattern.

    This class is a building block to define your own simple switches easily.
    Subclasses override the `get_switch_signal()` function that supplies the switch states inside a single period.

    frequency:
        The current frequency (measured in Hertz).
    phase:
        The initial phase angle (measured in rad).
    """
    frequency: float = 1.0
    phase: float = 0.0

    @property
    def T(self):
        """
        The period time :math:`T`.
        """
        return 1.0 / self.frequency

    @T.setter
    def T(self, value):
        self.frequency = 1.0 / value

    def get_phase_from_time(self, t):
        return t * 2 * pi * self.frequency + self.phase

    def switch_state(self, t: float) -> bool:
        return self.get_switch_signal(self.get_phase_from_time(t) % (2 * pi))

    def get_switch_signal(self, phase: float) -> bool:
        """
        Returns the signal.

        :param phase:
            The momentary angular phase, inside the range [0, 2pi).
        :return:
            The switch state.
        """
        raise NotImplementedError

    def next_event(self, vi: Callable[[float], np.ndarray], t1: float, t2: float) -> Optional[float]:
        interval1, phase1 = divmod(self.get_phase_from_time(t1), 2 * pi)
        interval2, phase2 = divmod(self.get_phase_from_time(t2), 2 * pi)

        intv_phase1 = phase1
        for p in range(int(interval1), int(interval2)):
            intv_phase2 = np.nextafter(2 * pi, 0)

            eventphase = self.next_switch_event(intv_phase1, intv_phase2)
            if eventphase is not None and 0 <= eventphase < 2 * pi:
                return (p + (eventphase - self.phase) / (2 * pi)) / self.frequency

            intv_phase1 = 0

        eventphase = self.next_switch_event(intv_phase1, phase2)
        return None if eventphase is None else (int(interval2) + (eventphase - self.phase) / (2 * pi)) / self.frequency

    def next_switch_event(self, phase1: float, phase2: float) -> Optional[float]:
        r"""
        Calculates the next switch event within a phase interval.

        Instead of event times, phases indicating the switch event are returned.
        They are properly translated to according simulation times.

        This function guarantees to serve phases in the range :math:`[0, 2\pi)`.

        :param phase1:
            Previous phase (measured in rad).
        :param phase2:
            Present phase (measured in rad).
        :return:
            The next phase at which a switch state change occurs, or None if nothing happens.
        """
        return None
