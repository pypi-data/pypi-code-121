# Copyright 2022 Boris Shminke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Bounded Lattice
===============
"""
from residuated_binars.algebraic_structure import BOT, TOP
from residuated_binars.axiom_checkers import (
    is_left_identity,
    is_left_zero,
    is_right_identity,
    is_right_zero,
)
from residuated_binars.lattice import Lattice


class BoundedLattice(Lattice):
    r"""
        a representation of a bounded lattice

    >>> join = {"0": {"0": "0", "1": "1"}, "1": {"0": "1", "1": "1"}}
    >>> meet = {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}}
    >>> lattice = Lattice("test", {"join": join, "meet": meet})
    >>> lattice.canonise_symbols()
    >>> BoundedLattice(lattice.label, lattice.operations)
    {'join': [[0, 1], [1, 1]], 'meet': [[0, 0], [0, 1]]}
    """

    def check_axioms(self) -> None:
        super().check_axioms()
        assert is_left_identity(self.operations["meet"], TOP)
        assert is_right_identity(self.operations["meet"], TOP)
        assert is_left_identity(self.operations["join"], BOT)
        assert is_right_identity(self.operations["join"], BOT)
        assert is_left_zero(self.operations["join"], TOP)
        assert is_right_zero(self.operations["join"], TOP)
        assert is_left_zero(self.operations["meet"], BOT)
        assert is_right_zero(self.operations["meet"], BOT)
