# Copyright 2021-2022 Boris Shminke
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
Abelian Group
==============
"""
from typing import Dict

from residuated_binars.algebraic_structure import AlgebraicStructure
from residuated_binars.axiom_checkers import (
    associative,
    commutative,
    is_left_identity,
    is_left_inverse,
    is_right_identity,
    is_right_inverse,
)


class AbelianGroup(AlgebraicStructure):
    """
    an Abelian group structure

    >>> add = {"0": {"0": "0"}}
    >>> group = AbelianGroup("test", {"add": add, "neg": {"0": "0"}})
    >>> print(group.mace4_format)
    0 + 0 = 0.
    neg(0) = 0.
    <BLANKLINE>
    """

    def check_axioms(self) -> None:
        assert associative(self.operations["add"])
        assert commutative(self.operations["add"])
        assert is_left_identity(self.operations["add"], "0")
        assert is_right_identity(self.operations["add"], "0")
        assert is_left_inverse(
            self.operations["add"], self.operations["neg"], "0"
        )
        assert is_right_inverse(
            self.operations["add"], self.operations["neg"], "0"
        )

    @property
    def operation_map(self) -> Dict[str, str]:
        return {"add": "+"}
