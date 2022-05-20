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
Pseudo-:math:`R_0` Algebra
==========================
"""
from residuated_binars.algebraic_structure import TOP
from residuated_binars.pseudo_weak_r0_algebra import PseudoWeakR0Algebra


class PseudoR0Algebra(PseudoWeakR0Algebra):
    """
    a representation of a peudo-:math:`R_0` algebra

    for more info look `here <https://doi.org/10.1155/2014/854168>`__

    >>> from residuated_binars.algebraic_structure import BOT
    >>> imp = {
    ...     BOT: {BOT: TOP, TOP: TOP, "C3": TOP, "C2": TOP},
    ...     TOP: {BOT: BOT, TOP: TOP, "C3": "C3", "C2": "C2"},
    ...     "C3": {BOT: "C2", TOP: TOP, "C3": TOP, "C2": "C3"},
    ...     "C2": {BOT: "C3", TOP: TOP, "C3": TOP, "C2": TOP}
    ... }
    >>> inv = {BOT: TOP, TOP: BOT, "C3": "C2", "C2": "C3"}
    >>> join = {
    ...     BOT: {BOT: BOT, TOP: TOP, "C3": "C3", "C2": "C2"},
    ...     TOP: {BOT: TOP, TOP: TOP, "C3": TOP, "C2": TOP},
    ...     "C3": {BOT: "C3", TOP: TOP, "C3": "C3", "C2": "C3"},
    ...     "C2": {BOT: "C2", TOP: TOP, "C3": "C3", "C2": "C2"}
    ... }
    >>> meet = {
    ...     BOT: {BOT: BOT, TOP: BOT, "C3": BOT, "C2": BOT},
    ...     TOP: {BOT: BOT, TOP: TOP, "C3": "C3", "C2": "C2"},
    ...     "C3": {BOT: BOT, TOP: "C3", "C3": "C3", "C2": "C2"},
    ...     "C2": {BOT: BOT, TOP: "C2", "C3": "C2", "C2": "C2"}
    ... }
    >>> operations = {"imp1": imp, "imp2": imp, "inv1": inv, "inv2": inv,
    ...     "join": join, "meet": meet}
    >>> PseudoR0Algebra("no P5", operations)
    Traceback (most recent call last):
     ...
    ValueError: P5 axiom doesn't hold
    >>> imp = {
    ...     BOT: {BOT: TOP, TOP: TOP, "C3": TOP, "C2": TOP},
    ...     TOP: {BOT: BOT, TOP: TOP, "C3": "C3", "C2": "C2"},
    ...     "C2": {BOT: "C3", TOP: TOP, "C2": TOP, "C3": "C3"},
    ...     "C3": {BOT: "C2", TOP: TOP, "C2": "C2", "C3": TOP}
    ... }
    >>> operations = {"imp1": imp, "imp2": imp, "inv1": inv, "inv2": inv,
    ...     "join": join, "meet": meet}
    >>> PseudoR0Algebra("no P5", operations)
    Traceback (most recent call last):
     ...
    ValueError: P4 axiom doesn't hold
    >>> imp = {
    ...     BOT: {BOT: TOP, TOP: TOP, "C3": TOP, "C2": TOP},
    ...     TOP: {BOT: BOT, TOP: TOP, "C3": "C3", "C2": "C2"},
    ...     "C2": {BOT: "C2", TOP: TOP, "C2": TOP, "C3": TOP},
    ...     "C3": {BOT: "C3", TOP: TOP, "C2": TOP, "C3": TOP}
    ... }
    >>> inv = {BOT: TOP, TOP: BOT, "C3": "C3", "C2": "C2"}
    >>> operations = {"imp1": imp, "imp2": imp, "inv1": inv, "inv2": inv,
    ...     "join": join, "meet": meet}
    >>> PseudoR0Algebra("no P5", operations)
    Traceback (most recent call last):
     ...
    ValueError: P3 axiom doesn't hold
    """

    def check_axioms(self) -> None:
        super().check_axioms()
        try:
            for one in self.operations["meet"].keys():
                for two in self.operations["meet"].keys():
                    assert (
                        self.operations["join"][
                            self.operations["imp1"][one][two]
                        ][
                            self.operations["imp2"][
                                self.operations["imp1"][one][two]
                            ][
                                self.operations["join"][
                                    self.operations["inv1"][one]
                                ][two]
                            ]
                        ]
                        == TOP
                    )
                    assert (
                        self.operations["join"][
                            self.operations["imp2"][one][two]
                        ][
                            self.operations["imp1"][
                                self.operations["imp2"][one][two]
                            ][
                                self.operations["join"][
                                    self.operations["inv2"][one]
                                ][two]
                            ]
                        ]
                        == TOP
                    )
        except AssertionError as error:
            raise ValueError("P5 axiom doesn't hold") from error
