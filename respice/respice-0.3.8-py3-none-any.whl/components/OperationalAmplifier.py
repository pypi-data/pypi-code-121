from __future__ import annotations

from dataclasses import dataclass, field
from typing import Hashable, List, Tuple, Sequence

import numpy as np

from .Branch import Branch, CurrentBranch, VoltageBranch
from .Component import Component


@dataclass(eq=False)
class OperationalAmplifier(Component):
    """
    Describes an (almost) ideal operational amplifier ("op-amp").

    An ideal op-amp has following idealizing characteristics:
    * Infinite open-loop gain (this is the only aspect which does not hold for this op-amp implementation, it's finite)
    * Infinite input impedance, and so zero input current
    * Zero input offset voltage
    * Infinite output voltage range
    * Infinite bandwidth with zero phase shift and infinite slew rate
    * Zero output impedance
    * Zero noise

    See also https://en.wikipedia.org/wiki/Operational_amplifier#Ideal_op-amps

    This component is connected in following order:
    * First two terminals denote the input voltages :math:`V_{in-}` and :math:`V_{in+}`.
    The difference between them is what is amplified.
    * The third terminal denotes GND (ground) or any reference potential you want to use.
    * The fourth terminal denotes the output voltage V_out (in reference to GND).

    g:
        Open loop gain. For real op-amps this value lies between 20000 and 200000.
    """

    @dataclass(eq=False)
    class InputBranch(CurrentBranch):
        def get_current(self, v_i: np.ndarray, t1: float, t2: float) -> float:
            return 0

        def get_jacobian(self, v_i: np.ndarray, t1: float, t2: float) -> Sequence[float]:
            return [0, 0]

    @dataclass(eq=False)
    class OutputBranch(VoltageBranch):
        def get_voltage(self, v_i: np.ndarray, t1: float, t2: float) -> float:
            return self.component.g * v_i[0]

        def get_jacobian(self, v_i: np.ndarray, t1: float, t2: float) -> Sequence[float]:
            return [self.component.g, 0]

    g: float = 100000
    _input_branch: InputBranch = field(init=False, repr=False)
    _output_branch: OutputBranch = field(init=False, repr=False)

    def __post_init__(self):
        self._input_branch = self.InputBranch(self)
        self._input_branch.name = 'input'
        self._output_branch = self.OutputBranch(self)
        self._output_branch.name = 'output'

    def connect(self,
                v_in_neg: Hashable,
                v_in_pos: Hashable,
                gnd: Hashable,
                v_out: Hashable) -> List[Tuple[Hashable, Hashable, Branch]]:
        """
        Connects the transistor.

        :param v_in_neg:
            The negative terminal of the input voltage to amplify.
        :param v_in_pos:
            The positive terminal of the input voltage to amplify.
        :param gnd:
            The ground / reference potential.
        :param v_out:
            The output voltage (in reference to given GND)
        """
        return [
            (v_in_neg, v_in_pos, self._input_branch),
            (gnd, v_out, self._output_branch),
        ]

    @property
    def input(self):
        return self._input_branch

    @property
    def output(self):
        return self._output_branch
