from dataclasses import dataclass
from math import pi, sqrt
from typing import Optional

from .PeriodicCurrentSource import PeriodicCurrentSource


@dataclass(eq=False)
class CurrentSourceRectangular(PeriodicCurrentSource):
    """
    A rectangular current source supply.

    By default the current toggles between `+amplitude` and `-amplitude`.
    To make the signal toggle between `0` and `a`, set `offset = amplitude = a / 2`.

    By default the duty cycle of the source is 0.5, meaning it toggles equally between min and max.
    The duty cycle determines how much time (relative) is spent between the min and max states.
    A value of 0 or below means the source becomes effectively a DC source serving constantly the minimum
    voltage. A value of 1 or above is effectively a constant DC source at maximum voltage.
    For example a value in between of 0.75 means that 75% of the period is spent at maximum voltage
    and the following 25% is minimum voltage.

    amplitude:
        The amplitude of the rectangular current (measured in Amperes).
    offset:
        The current offset of the signal (measured in Amperes).
    duty:
        The duty cycle. Meaningful values lie between 0 and 1.
    """
    amplitude: float = 1.0
    offset: float = 0.0
    duty: float = 0.5

    @property
    def effective_amplitude(self):
        r"""
        The effective amplitude (:math:`A_{RMS}`) depends not only on the amplitude, but also on the offset and duty
        cycle.
        According to the formula for RMS (see https://en.wikipedia.org/wiki/Root_mean_square and
        https://en.wikipedia.org/wiki/RMS_amplitude)

        .. math::

             A_{RMS} &= \sqrt{\frac{1}{T} \int_{0}^{T}{f^2(t) dt}} \\
                     &= \sqrt{
                            \frac{1}{T}
                                \left (
                                    \int_{0}^{\delta T}{(o + A)^2 dt} +
                                    \int_{\delta T}^{T}{(o - A)^2 dt}
                                \right )
                            } \\
                     &= \sqrt{
                            (o + A)^2 \delta T +
                            (o - A)^2 (1 - \delta) T
                        }

        :return:
            The effective amplitude current (measured in Amperes).
        """
        return sqrt(
            (self.offset + self.amplitude)**2 * self.duty +
            (self.offset - self.amplitude)**2 * (1 - self.duty)
        )

    def get_signal(self, phase: float) -> float:
        high = phase < 2 * pi * self.duty
        return self.amplitude * (1 if high else -1) + self.offset

    def next_signal_event(self, phase1: float, phase2: float) -> Optional[float]:
        if phase1 == 0.0:
            return 0.0

        dutyphase = self.duty * 2 * pi
        if phase1 <= dutyphase <= phase2:
            return dutyphase

        return None
