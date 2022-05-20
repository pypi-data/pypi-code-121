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
Pseudo-weak-:math:`R_0` Algebra
===============================
"""
from residuated_binars.algebraic_structure import BOT, TOP
from residuated_binars.axiom_checkers import (
    is_left_identity,
    left_distributive,
)
from residuated_binars.bounded_lattice import BoundedLattice


class PseudoWeakR0Algebra(BoundedLattice):
    """
    a representation of a peudo-weak-:math:`R_0` algebra

    for more info look `here <https://doi.org/10.1155/2014/854168>`__

    >>> join = {BOT: {BOT: BOT, TOP: TOP}, TOP: {BOT: TOP, TOP: TOP}}
    >>> meet = {BOT: {BOT: BOT, TOP: BOT}, TOP: {BOT: BOT, TOP: TOP}}
    >>> inv = {BOT: BOT, TOP: TOP}
    >>> imp = {BOT: {BOT: TOP, TOP: TOP}, TOP: {BOT: BOT, TOP: TOP}}
    >>> operations = {"imp1": imp, "imp2": imp, "inv1": inv, "inv2": inv,
    ...     "join": join, "meet": meet}
    >>> PseudoWeakR0Algebra("no P1", operations)
    Traceback (most recent call last):
     ...
    ValueError: P1 axiom doesn't hold
    >>> imp = {BOT: {BOT: TOP, TOP: TOP}, TOP: {BOT: TOP, TOP: TOP}}
    >>> operations = {"imp1": imp, "imp2": imp, "inv1": inv, "inv2": inv,
    ...     "join": join, "meet": meet}
    >>> PseudoWeakR0Algebra("no P1", operations)
    Traceback (most recent call last):
     ...
    ValueError: P2 axiom doesn't hold
    """

    def _check_p1(self) -> str:
        try:
            for one in self.operations["meet"].keys():
                for two in self.operations["meet"].keys():
                    assert (
                        self.operations["imp1"][one][two]
                        == self.operations["imp2"][
                            self.operations["inv1"][two]
                        ][self.operations["inv1"][one]]
                    )
                    assert (
                        self.operations["imp2"][one][two]
                        == self.operations["imp1"][
                            self.operations["inv2"][two]
                        ][self.operations["inv2"][one]]
                    )
            return " "
        except AssertionError:
            return "P1 axiom doesn't hold"

    def _check_p2(self) -> str:
        try:
            assert is_left_identity(self.operations["imp1"], TOP)
            assert is_left_identity(self.operations["imp2"], TOP)
            return " "
        except AssertionError:
            return "P2 axiom doesn't hold"

    def _check_p3(self) -> str:
        try:
            for i in self.operations["join"].keys():
                for j in self.operations["join"].keys():
                    for k in self.operations["join"].keys():
                        smaller = self.operations["imp1"][i][j]
                        greater = self.operations["imp1"][
                            self.operations["imp1"][k][i]
                        ][self.operations["imp1"][k][j]]
                        assert (
                            smaller == greater or smaller in self.more[greater]
                        )
                        smaller = self.operations["imp2"][i][j]
                        greater = self.operations["imp2"][
                            self.operations["imp2"][k][i]
                        ][self.operations["imp2"][k][j]]
                        assert (
                            smaller == greater or smaller in self.more[greater]
                        )
            return " "
        except AssertionError:
            return "P3 axiom doesn't hold"

    def _check_p4(self) -> str:
        try:
            assert left_distributive(
                self.operations["imp1"], self.operations["join"]
            )
            assert left_distributive(
                self.operations["imp2"], self.operations["join"]
            )
            return " "
        except AssertionError:
            return "P4 axiom doesn't hold"

    def check_axioms(self) -> None:
        super().check_axioms()
        assert (
            self.operations["inv1"][self.operations["inv2"][BOT]] == BOT
            and self.operations["inv2"][self.operations["inv1"][BOT]] == BOT
            and self.operations["inv1"][self.operations["inv2"][TOP]] == TOP
            and self.operations["inv2"][self.operations["inv1"][TOP]] == TOP
        ), "Pseudo-inverse axioms don't hold"
        res = " ".join(
            (
                self._check_p1(),
                self._check_p2(),
                self._check_p3(),
                self._check_p4(),
            )
        ).strip()
        if res != "":
            raise ValueError(res)
