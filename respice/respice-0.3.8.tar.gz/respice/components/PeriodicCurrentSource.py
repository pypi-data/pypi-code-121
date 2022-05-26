from dataclasses import dataclass
from math import pi
from typing import Optional, Callable

import numpy as np

from .TwoTerminalCurrentComponent import TwoTerminalCurrentComponent


@dataclass(eq=False)
class PeriodicCurrentSource(TwoTerminalCurrentComponent):
    """
    A periodic current supply.

    This class is a building block to define your own voltage/current invariant periodic sources easily. Subclasses
    override the `get_signal()` function that supplies the signal values inside a single period.

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

    def get_current(self, v: float, t1: float, t2: float) -> float:
        return self.get_signal(self.get_phase_from_time(t2) % (2 * pi))

    def get_jacobian(self, v: float, t1: float, t2: float) -> float:
        return 0

    def get_signal(self, phase: float) -> float:
        """
        Returns the signal.

        :param phase:
            The momentary angular phase, inside the range [0, 2pi).
        :return:
            The signal value at `phase`.
        """
        raise NotImplementedError

    def next_event(self, v: Callable[[float], np.ndarray], t1: float, t2: float) -> Optional[float]:
        interval1, phase1 = divmod(self.get_phase_from_time(t1), 2 * pi)
        interval2, phase2 = divmod(self.get_phase_from_time(t2), 2 * pi)

        intv_phase1 = phase1
        intv_phase2 = np.nextafter(2 * pi, 0)
        for p in range(int(interval1), int(interval2)):
            eventphase = self.next_signal_event(intv_phase1, intv_phase2)
            if eventphase is not None and 0 <= eventphase < 2 * pi:
                return (p + (eventphase - self.phase) / (2 * pi)) / self.frequency

            intv_phase1 = 0

        eventphase = self.next_signal_event(intv_phase1, phase2)
        return None if eventphase is None else (int(interval2) + (eventphase - self.phase) / (2 * pi)) / self.frequency

    def next_signal_event(self, phase1: float, phase2: float) -> Optional[float]:
        r"""
        If a source is discontinuous, this function should be used to indicate such discontinuities
        as events.

        Instead of event times, phases indicating the event are returned.
        They are properly translated to according simulation times.

        This function guarantees to serve phases in the range :math:`[0, 2\pi)`.

        :param phase1:
            Previous phase (measured in rad).
        :param phase2:
            Present phase (measured in rad).
        :return:
            The next phase at which an event occurs, or None if no event happens.
        """
        return None
