from dataclasses import dataclass
from math import sin, sqrt
from typing import Optional

from respice.components.PeriodicVoltageSource import PeriodicVoltageSource


@dataclass(eq=False)
class VoltageSourceHalfWaveAC(PeriodicVoltageSource):
    """
    A half wave / rectified AC voltage supply.

    You might alternatively set the amplitude by specifying an effective voltage.
    Be sure to assign to the property `effective_amplitude` after initialization.

    The frequency is relative to a half-wave, i.e. a single period contains a single mount.

    amplitude:
        The voltage amplitude of the sine emitted by the supply (measured in Volts).
    """
    amplitude: float = 1.0

    @property
    def effective_amplitude(self):
        r"""
        The effective amplitude (:math:`A_{RMS}`) is easily derived
        according to the formula for RMS (see https://en.wikipedia.org/wiki/Root_mean_square and
        https://en.wikipedia.org/wiki/RMS_amplitude) and is equal to the normal sine-wave case:

        .. math::

             A_{RMS} &= \sqrt{\frac{1}{T} \int_{0}^{T}{f^2(t) dt}} \\
                     &= A \cdot
                        \sqrt{
                            \frac{1}{2 \pi}
                                \left (
                                    \int_{0}^{T}{|\sin{(t)}|^2 dt}
                                \right )
                            } \\
                     &= A / \sqrt{2}

        :return:
            The effective voltage (measured in Volts).
        """
        return self.amplitude / sqrt(2)

    @effective_amplitude.setter
    def effective_amplitude(self, value: float):
        r"""
        Sets the amplitude of this supply by means of an effective value (RMS).

        This function just multiplies the given value with sqrt(2).

        .. math::

             A = \sqrt{2} \cdot A_{RMS}

        :param value:
            The effective value.
        """
        self.amplitude = value * sqrt(2)

    def get_signal(self, phase: float) -> float:
        return self.amplitude * sin(0.5 * phase)

    def next_signal_event(self, phase1: float, phase2: float) -> Optional[float]:
        if phase1 == 0.0:
            return 0.0
