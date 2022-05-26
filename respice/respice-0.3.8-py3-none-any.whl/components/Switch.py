from __future__ import annotations

from dataclasses import dataclass, field
from typing import Hashable, List, Tuple

from .Branch import Branch, SwitchBranch
from .Component import Component


@dataclass(eq=False)
class Switch(Component):
    """
    The base class for all simple switches.
    """
    _switch: _SwitchBranch = field(init=False, repr=False)

    @dataclass(eq=False)
    class _SwitchBranch(SwitchBranch):
        """
        The branch that represents the simple switch.

        Effectively mirrors all functions like `get_switch_state` back to the parent component.
        """
        def switch_state(self, t: float) -> bool:
            return self.component.switch_state(t)

        def __str__(self):
            return f'{str(self.component)}'

    def __post_init__(self):
        self._switch = self._SwitchBranch(self)

    def connect(self, terminal1: Hashable, terminal2: Hashable) -> List[Tuple[Hashable, Hashable, Branch]]:
        return [(terminal1, terminal2, self._switch)]

    def switch_state(self, t: float) -> bool:
        raise NotImplementedError

    @property
    def default_branch(self):
        """
        Returns the one and only branch of a two terminal component.
        """
        return self._switch
