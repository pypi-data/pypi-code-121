from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Hashable, Tuple, Sequence

import numpy as np

from .Branch import Branch, VoltageBranch
from .Component import Component


@dataclass(eq=False)
class TwoTerminalVoltageComponent(Component):
    """
    The base class for all two-terminal electrical components that have a current-to-voltage characteristic.

    This class avoids you to maintain `Branch`s for this simple two-terminal case. Instead of creating a branch,
    you can immediately override methods like `get_voltage` or `update` and access voltages and currents via this
    component itself (`component.v` and `component.i`).
    """
    _branch: _TwoTerminalBranch = field(init=False, repr=False)

    @dataclass(eq=False)
    class _TwoTerminalBranch(VoltageBranch):
        """
        The branch that represents the two-terminal component.

        Effectively mirrors all functions like `get_current` back to the parent component.
        """
        def get_voltage(self, v_i: np.ndarray, t1: float, t2: float) -> float:
            return self.component.get_voltage(v_i[0], t1, t2)

        def get_jacobian(self, v_i: np.ndarray, t1: float, t2: float) -> Sequence[float]:
            return [self.component.get_jacobian(v_i[0], t1, t2)]

        def __str__(self):
            return f'{str(self.component)}'

    def __post_init__(self):
        self._branch = self._TwoTerminalBranch(self)

    def connect(self, terminal1: Hashable, terminal2: Hashable) -> List[Tuple[Hashable, Hashable, Branch]]:
        return [(terminal1, terminal2, self._branch)]

    def get_voltage(self, i: float, t1: float, t2: float) -> float:
        """
        Calculated voltage depending on given current and time step.

        Shall return the voltage at present point in time `t2`.

        :param i:
            Current (measured in Ampere).
        :param t1:
            Previous point in time (measured in seconds).
        :param t2:
            Present point in time (measured in seconds).
        :return:
            The voltage (measured in Volts).
        """
        raise NotImplementedError

    def get_jacobian(self, i: float, t1: float, t2: float) -> float:
        """
        Returns the derivative (a.k.a. 1D Jacobian) of `get_voltage` over the current `i`.

        For the numerical algorithm to quickly converge with more accuracy, it is necessary for electrical circuit
        problems to supply the derivations of each current / voltage function.

        See also https://en.wikipedia.org/wiki/Derivative and
        https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant

        :param i:
            Current (measured in Ampere).
        :param t1:
            Previous point in time (measured in seconds).
        :param t2:
            Present point in time (measured in seconds).
        :return:
            The derivative value (measured in Volt per second).
        """
        raise NotImplementedError

    @property
    def default_branch(self):
        """
        Returns the one and only branch of a two terminal component.
        """
        return self._branch
