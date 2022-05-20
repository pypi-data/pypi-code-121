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
Boolean Ring
=============
"""
from typing import Dict

from residuated_binars.abelian_group import AbelianGroup
from residuated_binars.axiom_checkers import (
    associative,
    idempotent,
    is_left_identity,
    is_right_identity,
    left_distributive,
    right_distributive,
)


class BooleanRing(AbelianGroup):
    """
    a Boolean ring structure

    >>> add = {"0": {"0": "0", "1": "1"}, "1": {"0": "1", "1": "0"}}
    >>> neg = {"0": "0", "1": "1"}
    >>> mult = {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}}
    >>> ring = BooleanRing("test", {"add": add, "neg": neg, "mult": mult})
    >>> print(ring.mace4_format)
    0 + 0 = 0.
    0 + 1 = 1.
    1 + 0 = 1.
    1 + 1 = 0.
    neg(0) = 0.
    neg(1) = 1.
    0 * 0 = 0.
    0 * 1 = 0.
    1 * 0 = 0.
    1 * 1 = 1.
    <BLANKLINE>
    """

    def check_axioms(self) -> None:
        super().check_axioms()
        assert associative(self.operations["mult"])
        assert is_left_identity(self.operations["mult"], "1")
        assert is_right_identity(self.operations["mult"], "1")
        assert left_distributive(
            self.operations["mult"], self.operations["add"]
        )
        assert right_distributive(
            self.operations["mult"], self.operations["add"]
        )
        assert idempotent(self.operations["mult"])

    @property
    def operation_map(self) -> Dict[str, str]:
        return {"add": "+", "mult": "*"}
