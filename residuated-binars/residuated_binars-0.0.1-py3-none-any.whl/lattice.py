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
Lattice
========
"""
from typing import Dict, List, Tuple

import graphviz

from residuated_binars.algebraic_structure import BOT, TOP, AlgebraicStructure
from residuated_binars.axiom_checkers import absorbs, associative, commutative


class Lattice(AlgebraicStructure):
    r"""
        a representation of a lattice

    >>> join = {"0": {"0": "0", "1": "1"}, "1": {"0": "1", "1": "1"}}
    >>> meet = {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}}
    >>> lattice = Lattice("test", {"join": join, "meet": meet})
    >>> print(lattice.mace4_format)
    0 v 0 = 0.
    0 v 1 = 1.
    1 v 0 = 1.
    1 v 1 = 1.
    0 ^ 0 = 0.
    0 ^ 1 = 0.
    1 ^ 0 = 0.
    1 ^ 1 = 1.
    <BLANKLINE>
    >>> lattice.canonise_symbols()
    >>> print(lattice.graphviz_repr)
    graph {
        "⟙" -- "⟘"
    }
    >>> join["0"]["1"] = "0"
    >>> Lattice("test", {"join": join, "meet": meet})
    Traceback (most recent call last):
     ...
    ValueError: join is not commutative
    >>> join["0"]["1"] = "1"
    >>> meet["0"]["1"] = "1"
    >>> Lattice("test", {"join": join, "meet": meet})
    Traceback (most recent call last):
     ...
    ValueError: meet is not commutative
    >>> meet["0"]["1"] = "0"
    >>> join["0"]["0"] = "1"
    >>> Lattice("test", {"join": join, "meet": meet})
    Traceback (most recent call last):
     ...
    ValueError: absorption laws fail
    >>> join = {'0': {'0': '1', '1': '0'}, '1': {'0': '0', '1': '0'}}
    >>> meet = {'0': {'0': '0', '1': '0'}, '1': {'0': '0', '1': '1'}}
    >>> Lattice("test", {"join": join, "meet": meet})
    Traceback (most recent call last):
     ...
    ValueError: join is not associative
    >>> join = {'0': {'0': '0', '1': '0'}, '1': {'0': '0', '1': '1'}}
    >>> meet = {'0': {'0': '1', '1': '0'}, '1': {'0': '0', '1': '0'}}
    >>> Lattice("test", {"join": join, "meet": meet})
    Traceback (most recent call last):
     ...
    ValueError: meet is not associative
    """

    def check_axioms(self) -> None:
        self._check_commutativity_and_associativity()
        if not absorbs(
            self.operations["meet"], self.operations["join"]
        ) or not absorbs(self.operations["join"], self.operations["meet"]):
            raise ValueError("absorption laws fail")

    def _check_commutativity_and_associativity(self):
        if not commutative(self.operations["join"]):
            raise ValueError("join is not commutative")
        if not commutative(self.operations["meet"]):
            raise ValueError("meet is not commutative")
        if not associative(self.operations["join"]):
            raise ValueError("join is not associative")
        if not associative(self.operations["meet"]):
            raise ValueError("meet is not associative")

    @property
    def operation_map(self) -> Dict[str, str]:
        return {"meet": "^", "join": "v"}

    @property
    def more(self) -> Dict[str, List[str]]:
        """
        :returns: some representation of a 'more' relation of a lattice reduct
            of the lattice
        """
        relation: Dict[str, List[str]] = {}
        for one in self.symbols:
            relation[one] = []
            for two in self.symbols:
                if self.operations["meet"][one][two] == two and one != two:
                    relation[one].append(two)
        return relation

    @property
    def hasse(self) -> List[Tuple[str, str]]:
        """
        :returns: some representation of a Hasse diagram of a lattice reduct of
            the lattice
        """
        more = {
            pair[0]: pair[1]
            for pair in sorted(
                self.more.items(),
                key=lambda key_value: -len(key_value[1]),
            )
        }
        hasse = []
        for higher in more:
            nearest = set(more[higher])
            for lower in more[higher]:
                nearest = nearest.difference(set(more[lower]))
            hasse += [(higher, neighbour) for neighbour in list(nearest)]
        return hasse

    @property
    def graphviz_repr(self) -> str:
        """
        :returns: a representation usable by ``graphviz`` of a Hasse diagram of
            a lattice reduct of the lattice
        """
        graph = graphviz.Graph()
        for pair in self.hasse:
            graph.edge(pair[0], pair[1])
        return graph

    def canonise_symbols(self) -> None:
        """
        renumerate lattice's items in a canonical way
        """
        symbol_map = {
            pair[1]: pair[0]
            for pair in zip(
                [BOT]
                + [chr(ord("a") + i) for i in range(self.cardinality - 2)]
                + [TOP],
                [
                    key
                    for key, value in sorted(
                        self.more.items(),
                        key=lambda key_value: (
                            len(key_value[1]),
                            key_value[0],
                        ),
                    )
                ],
            )
        }
        self.remap_symbols(symbol_map)
