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
Algebraic Structure
====================
"""
from typing import Any, Dict, List, Union

CayleyTable = Dict[str, Dict[str, str]]
TOP = r"⟙"
BOT = r"⟘"


class AlgebraicStructure:
    r"""
        a base class for difference algebraic structures

    >>> magma_with_involution = AlgebraicStructure(
    ...     label="test",
    ...     operations={
    ...         "mult": {"0": {"0": "0", "1": "1"}, "1": {"0": "1", "1": "1"}},
    ...         "invo": {"0": "1", "1": "0"}
    ...     }
    ... )
    >>> magma_with_involution
    {'mult': [[0, 1], [1, 1]], 'invo': [1, 0]}
    >>> magma_with_involution.symbols
    ['0', '1']
    >>> magma_with_involution.remap_symbols({"0": "c1", "1": "c2"})
    >>> magma_with_involution
    {'mult': [[0, 1], [1, 1]], 'invo': [1, 0]}
    >>> magma_with_involution.symbols
    ['c1', 'c2']
    >>> print(magma_with_involution.mace4_format)
    mult(c1, c1) = c1.
    mult(c1, c2) = c2.
    mult(c2, c1) = c2.
    mult(c2, c2) = c2.
    invo(c1) = c2.
    invo(c2) = c1.
    <BLANKLINE>
    >>> class Magma(AlgebraicStructure):
    ...     ''' an example with redefined operation symbol '''
    ...
    ...     @property
    ...     def operation_map(self) -> Dict[str, str]:
    ...         return {"mult": "*"}
    >>> magma = Magma("test", {"mult": {"c": {"c": "c"}}})
    >>> print(magma.mace4_format)
    c * c = c.
    <BLANKLINE>
    """

    def __init__(
        self,
        label: str,
        operations: Dict[str, Dict[str, Any]],
    ):
        self.label = label
        self.operations = operations
        self.check_axioms()

    def check_axioms(self) -> None:
        """
        check axioms specific to that algebraic structure. If any axiom fails,
        raise an error

        :returns:
        """

    @property
    def cardinality(self) -> int:
        """
        :returns: number of items in the algebraic structure
        """
        return len(next(iter(self.operations.items()))[1].keys())

    def remap_symbols(self, symbol_map: Dict[str, str]) -> None:
        """rename symbols in a given way"""
        for op_label, operation in self.operations.items():
            if isinstance(next(iter(operation.items()))[1], Dict):
                new_table: CayleyTable = {}
                for one in symbol_map.keys():
                    new_table[symbol_map[one]] = {}
                    for two in symbol_map.keys():
                        new_table[symbol_map[one]][
                            symbol_map[two]
                        ] = symbol_map[operation[one][two]]
                self.operations[op_label] = new_table
            else:
                new_op: Dict[str, str] = {}
                for one in symbol_map.keys():
                    new_op[symbol_map[one]] = symbol_map[operation[one]]
                self.operations[op_label] = new_op

    @property
    def symbols(self) -> List[str]:
        """
        :returns: a list of symbols denoting items of an algebraic structure
        """
        keys = list(next(iter(self.operations.items()))[1].keys())
        pure_keys = keys.copy()
        if TOP in pure_keys:
            pure_keys.remove(TOP)
        if BOT in pure_keys:
            pure_keys.remove(BOT)
        return (
            ([BOT] if BOT in keys else [])
            + list(sorted(pure_keys))
            + ([TOP] if TOP in keys else [])
        )

    @property
    def operation_map(self) -> Dict[str, str]:
        """
        :returns: a map from operation labels (for functional notation) to
            operation symbols (for infix notation)
        """
        return {}

    @property
    def mace4_format(self) -> str:
        """
        represent the algebraic structure in ``Prover9/Mace4`` format
        :returns: a string representation
        """
        result = ""
        for op_label, operation in self.operations.items():
            op_symbol = self.operation_map.get(op_label, None)
            if isinstance(list(operation.items())[0][1], Dict):
                for i in self.symbols:
                    for j in self.symbols:
                        if op_symbol is not None:
                            result += (
                                f"{i} {op_symbol} {j} = {operation[i][j]}.\n"
                            )
                        else:
                            result += (
                                f"{op_label}({i}, {j}) = {operation[i][j]}.\n"
                            )
            else:
                for i in self.symbols:
                    result += f"{op_label}({i}) = {operation[i]}.\n"
        return result

    def _operation_tabular_view(
        self, operation: Dict[str, Any]
    ) -> Union[List[List[int]], List[int]]:
        inverse_index = {symbol: i for i, symbol in enumerate(self.symbols)}
        if isinstance(next(iter(operation.items()))[1], Dict):
            table: List[List[int]] = []
            for one in self.symbols:
                table.append([])
                for two in self.symbols:
                    table[inverse_index[one]].append(
                        inverse_index[operation[one][two]]
                    )
            return table
        new_operation: List[int] = list(range(len(operation)))
        for one in self.symbols:
            new_operation[inverse_index[one]] = inverse_index[operation[one]]
        return new_operation

    @property
    def tabular_format(self) -> Dict[str, Union[List[List[int]], List[int]]]:
        """
        :returns: a dictionary of Cayley tables as lists of lists
        """
        return {
            op_label: self._operation_tabular_view(operation)
            for op_label, operation in self.operations.items()
        }

    def __repr__(self):
        return str(self.tabular_format)
