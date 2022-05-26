from __future__ import annotations

from dataclasses import dataclass, field
from typing import Hashable, List, Tuple, Sequence

import numpy as np

from .Branch import Branch, VoltageBranch, CurrentBranch
from .Component import Component


@dataclass(eq=False)
class CoupledInductance(Component):
    """
    Represents an ideally mutually coupled coil.

    n1:
        The number of windings on coil 1 ("left-hand").
    n1:
        The number of windings on coil 2 ("right-hand").
    """

    @dataclass(eq=False)
    class CoupledInductanceCoil1(VoltageBranch):
        def get_voltage(self, v_i: np.ndarray, t1: float, t2: float) -> float:
            return v_i[1] * self.component.n1 / self.component.n2

        def get_jacobian(self, v_i: np.ndarray, t1: float, t2: float) -> Sequence[float]:
            return [0, self.component.n1 / self.component.n2]

    @dataclass(eq=False)
    class CoupledInductanceCoil2(CurrentBranch):
        def get_current(self, v_i: np.ndarray, t1: float, t2: float) -> float:
            return v_i[0] * self.component.n1 / self.component.n2

        def get_jacobian(self, v_i: np.ndarray, t1: float, t2: float) -> Sequence[float]:
            return [self.component.n1 / self.component.n2, 0]

    n1: int
    n2: int
    coil1: CoupledInductanceCoil1 = field(init=False, repr=False)
    coil2: CoupledInductanceCoil2 = field(init=False, repr=False)

    def __post_init__(self):
        self.coil1 = self.CoupledInductanceCoil1(self)
        self.coil1.name = 'coil1'
        self.coil2 = self.CoupledInductanceCoil2(self)
        self.coil1.name = 'coil2'

    def connect(self,
                coil1_terminal1: Hashable,
                coil1_terminal2: Hashable,
                coil2_terminal1: Hashable,
                coil2_terminal2: Hashable) -> List[Tuple[Hashable, Hashable, Branch]]:
        """
        Connects the mutually coupled inductance.

        :param coil1_terminal1:
            Terminal 1 of the first coil.
        :param coil1_terminal2:
            Terminal 2 of the first coil.
        :param coil2_terminal1:
            Terminal 1 of the second coil.
        :param coil2_terminal2:
            Terminal 2 of the second coil.
        """
        return [
            (coil1_terminal1, coil1_terminal2, self.coil1),
            (coil2_terminal1, coil2_terminal2, self.coil2),
        ]
