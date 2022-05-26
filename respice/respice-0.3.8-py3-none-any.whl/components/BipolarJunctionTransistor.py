from __future__ import annotations

from dataclasses import dataclass, field
from math import exp
from typing import Hashable, List, Tuple, Sequence

import numpy as np

from .Branch import Branch, CurrentBranch
from .Component import Component


@dataclass(eq=False)
class BipolarJunctionTransistor(Component):
    """
    Describes a bipolar junction transistor.

    This component uses the simplified large-signal Ebers-Moll model
    (see https://en.wikipedia.org/wiki/Bipolar_junction_transistor#Ebers%E2%80%93Moll_model).

    This component is connected in B-C-E order. The first given terminal connects to the base, the second one to
    the collector and the last one to the emitter.

    For convenience you can immediately access the currents at the B/C/E terminals by using the `i_b`, `i_c` and `i_e`
    properties respectively. Mind their current direction. Also you can access `v_cb` (C -> B), `v_be` (B -> E)  and
    `v_ce` (C -> E) to get the voltage drops.

    i_es:
        Reverse saturation current I_ES of the base–emitter diode (on the order of 10^−15 to 10^−12 amperes).
    alpha_f:
        Common base forward short-circuit current gain (usually 0.98 to 0.998)
    v_t:
        Thermal voltage V_T. For approximate room temperate 300K this value is 25.85mV (0.02585V). This is default.
    """

    @dataclass(eq=False)
    class CollectorBaseBranch(CurrentBranch):
        def get_current(self, v_i: np.ndarray, t1: float, t2: float) -> float:
            return self.component.i_es * (exp(v_i[1] / self.component.v_t) - 1) * self.component.alpha_f

        def get_jacobian(self, v_i: np.ndarray, t1: float, t2: float) -> Sequence[float]:
            return [
                0,
                self.component.i_es / self.component.v_t * exp(v_i[1] / self.component.v_t) * self.component.alpha_f
            ]

    @dataclass(eq=False)
    class BaseEmitterBranch(CurrentBranch):
        def get_current(self, v_i: np.ndarray, t1: float, t2: float) -> float:
            return self.component.i_es * (exp(v_i[1] / self.component.v_t) - 1)

        def get_jacobian(self, v_i: np.ndarray, t1: float, t2: float) -> Sequence[float]:
            return [0, self.component.i_es / self.component.v_t * exp(v_i[1] / self.component.v_t)]

    i_es: float
    alpha_f: float
    v_t: float = 0.02585
    _collector_base_branch: CollectorBaseBranch = field(init=False, repr=False)
    _base_emitter_branch: BaseEmitterBranch = field(init=False, repr=False)

    def __post_init__(self):
        self._collector_base_branch = self.CollectorBaseBranch(self)
        self._collector_base_branch.name = 'CB'
        self._base_emitter_branch = self.BaseEmitterBranch(self)
        self._base_emitter_branch.name = 'BE'

    def connect(self,
                base: Hashable,
                collector: Hashable,
                emitter: Hashable) -> List[Tuple[Hashable, Hashable, Branch]]:
        """
        Connects the transistor.

        :param base:
            The base (B) terminal.
        :param collector:
            The collector (C) terminal.
        :param emitter:
            The emitter (E) terminal.
        """
        return [
            (collector, base, self._collector_base_branch),
            (base, emitter, self._base_emitter_branch),
        ]
