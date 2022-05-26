from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


@dataclass(eq=False)
class Branch:
    """
    The most basic element describing the relation between two potentials/terminals.

    Please use the more specific implementations `VoltageDrivenEdge` and `CurrentDrivenEdge` instead. Subclassing
    this base `Edge` class will have no meaning to the simulation algorithm that will simply ignore everything else.

    name:
        An optional name to set for the component. Can be set after initialization.
    """
    component: Component = field(repr=False)
    name: str = field(default=None, init=False)

    def __str__(self):
        branch_str = repr(self) if self.name is None or self.name == '' else self.name
        return f'{str(self.component)}/{branch_str}'


@dataclass(eq=False)
class CurrentBranch(Branch):
    def get_current(self, v_i: np.ndarray, t1: float, t2: float) -> float:
        """
        Calculated current depending on given voltages / currents and time steps.

        Shall return the current at present point in time `t2`.

        :param v_i:
            Voltages (measured in Volts) and currents (measured in Ampere). A vector filled with the potentials and
            branch currents as specified in the edges returned by `connect` (in order). See also `Element.connect`.
        :param t1:
            Previous point in time (measured in seconds).
        :param t2:
            Present point in time (measured in seconds).
        :return:
            The current (measured in Ampere).
        """
        raise NotImplementedError

    def get_jacobian(self, v_i: np.ndarray, t1: float, t2: float) -> Sequence[float]:
        """
        Returns the Jacobian matrix (i.e. the "gradient matrix") of the current function.

        For the numerical algorithm to quickly converge with more accuracy, it is necessary for electrical circuit
        problems to supply the derivations of each current / voltage function.

        This function specifically is supposed to return an array of derivatives instead of a matrix. Depending on the
        coupled branches specified by the holding component, the derivatives have to be returned in the same order.

        See also https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant

        Note that the Jacobian matrix must not include derivations over `t1` and `t2`.

        :param v_i:
            Voltages (measured in Volts) and currents (measured in Ampere). A vector filled with the potentials and
            branch currents as specified in the edges returned by `connect` (in order). See also `Element.connect`.
        :param t1:
            Previous point in time (measured in seconds).
        :param t2:
            Present point in time (measured in seconds).
        :return:
            The Jacobian (measured in Ampere per second).
        """
        raise NotImplementedError


@dataclass(eq=False)
class VoltageBranch(Branch):
    def get_voltage(self, v_i: np.ndarray, t1: float, t2: float) -> float:
        """
        Calculated current depending on given voltages / currents and time steps.

        Shall return the voltage at present point in time `t2`.

        :param v_i:
            Voltages (measured in Volts) and currents (measured in Ampere). A vector filled with the potentials and
            branch currents as specified in the edges returned by `connect` (in order). See also `Element.connect`.
        :param t1:
            Previous point in time (measured in seconds).
        :param t2:
            Present point in time (measured in seconds).
        :return:
            The current (measured in Ampere).
        """
        raise NotImplementedError

    def get_jacobian(self, v_i: np.ndarray, t1: float, t2: float) -> Sequence[float]:
        """
        Returns the Jacobian matrix (i.e. the "gradient matrix") of the voltage function.

        For the numerical algorithm to quickly converge with more accuracy, it is necessary for electrical circuit
        problems to supply the derivations of each current / voltage function.

        This function specifically is supposed to return an array of derivatives instead of a matrix. Depending on the
        coupled branches specified by the holding component, the derivatives have to be returned in the same order.

        See also https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant

        Note that the Jacobian matrix must not include derivations over `t1` and `t2`.

        :param v_i:
            Voltages (measured in Volts) and currents (measured in Ampere). A vector filled with the potentials and
            branch currents as specified in the edges returned by `connect` (in order). See also `Element.connect`.
        :param t1:
            Previous point in time (measured in seconds).
        :param t2:
            Present point in time (measured in seconds).
        :return:
            The Jacobian (measured in Volt per second).
        """
        raise NotImplementedError


@dataclass(eq=False)
class SwitchBranch(Branch):
    def switch_state(self, t: float) -> bool:
        """
        The current switch state at time `t`.

        :param t:
            Absolute point in time (measured in seconds).
        :return:
            `True` if switch is on, `False` if off.
        """
        raise NotImplementedError
