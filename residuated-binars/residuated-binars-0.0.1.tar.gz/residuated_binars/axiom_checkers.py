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
Axiom Checkers
===============
"""
from typing import Dict

from residuated_binars.algebraic_structure import CayleyTable


def associative(cayley_table: CayleyTable) -> bool:
    """
    >>> associative({"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "0"}})
    True
    >>> associative({"0": {"0": "1", "1": "0"}, "1": {"0": "0", "1": "0"}})
    False

    :param cayley_table: a multiplication table of a binary operation
    :returns: whether the operation is associative or not
    """
    for one in cayley_table.keys():
        for two in cayley_table.keys():
            for three in cayley_table.keys():
                if (
                    cayley_table[one][cayley_table[two][three]]
                    != cayley_table[cayley_table[one][two]][three]
                ):
                    return False
    return True


def is_left_identity(cayley_table: CayleyTable, identity: str) -> bool:
    """
    >>> is_left_identity(
    ...     {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}}, "1"
    ... )
    True
    >>> is_left_identity(
    ...     {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}}, "0"
    ... )
    False

    :param cayley_table: a multiplication table of a binary operation
    :param identity: a symbol for identity
    :returns: whether ``identity`` is a left identity for a Cayley table
    """
    for one in cayley_table.keys():
        if cayley_table[identity][one] != one:
            return False
    return True


def is_right_identity(cayley_table: CayleyTable, identity: str) -> bool:
    """
    >>> is_right_identity(
    ...     {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}}, "1"
    ... )
    True
    >>> is_right_identity(
    ...     {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}}, "0"
    ... )
    False

    :param cayley_table: a multiplication table of a binary operation
    :param identity: a symbol for identity
    :returns: whether ``identity`` is a right identity for a Cayley table
    """
    for one in cayley_table.keys():
        if cayley_table[one][identity] != one:
            return False
    return True


def is_left_inverse(
    cayley_table: CayleyTable, inverse: Dict[str, str], identity: str
) -> bool:
    """
    >>> op = {"0": {"0": "1", "1": "1"}, "1": {"0": "1", "1": "1"}}
    >>> inv = {"0": "1", "1": "1"}
    >>> is_left_inverse(op, inv, "1")
    True
    >>> is_left_inverse(op, inv, "0")
    False

    :param cayley_table: a multiplication table of a binary operation
    :param inverse: a map for the operation of inversion
    :param identity: a symbol for identity
    :returns: whether ``inverse`` is a left inverse for a Cayley table
    """
    for one in cayley_table.keys():
        if cayley_table[inverse[one]][one] != identity:
            return False
    return True


def is_right_inverse(
    cayley_table: CayleyTable, inverse: Dict[str, str], identity: str
) -> bool:
    """
    >>> op = {"0": {"0": "1", "1": "1"}, "1": {"0": "1", "1": "1"}}
    >>> inv = {"0": "1", "1": "1"}
    >>> is_right_inverse(op, inv, "1")
    True
    >>> is_right_inverse(op, inv, "0")
    False

    :param cayley_table: a multiplication table of a binary operation
    :param inverse: a map for the operation of inversion
    :param identity: a symbol for identity
    :returns: whether ``inverse`` is a right inverse for a Cayley table
    """
    for one in cayley_table.keys():
        if cayley_table[one][inverse[one]] != identity:
            return False
    return True


def commutative(cayley_table: CayleyTable) -> bool:
    """
    >>> commutative({"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "0"}})
    True
    >>> commutative({"0": {"0": "0", "1": "1"}, "1": {"0": "0", "1": "0"}})
    False

    :param cayley_table: a multiplication table of a binary operation
    :returns: whether the operation is commutative or not
    """
    for one in cayley_table.keys():
        for two in cayley_table.keys():
            if cayley_table[one][two] != cayley_table[two][one]:
                return False
    return True


def idempotent(cayley_table: CayleyTable) -> bool:
    """
    >>> idempotent({"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}})
    True
    >>> idempotent({"0": {"0": "0", "1": "1"}, "1": {"0": "0", "1": "0"}})
    False

    :param cayley_table: a multiplication table of a binary operation
    :returns: whether the operation is idempotent or not
    """
    for one in cayley_table.keys():
        if cayley_table[one][one] != one:
            return False
    return True


def left_distributive(table1: CayleyTable, table2: CayleyTable) -> bool:
    """
    >>> operation = {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "0"}}
    >>> left_distributive(operation, operation)
    True
    >>> operation = {"0": {"0": "1", "1": "0"}, "1": {"0": "0", "1": "0"}}
    >>> left_distributive(operation, operation)
    False

    :param table1: a multiplication table of a binary operation
    :param table2: a multiplication table of another binary operation
    :returns: whether the first operation is left distributive with respect to
        the second one or not
    """
    for one in table1.keys():
        for two in table1.keys():
            for three in table1.keys():
                if (
                    table1[one][table2[two][three]]
                    != table2[table1[one][two]][table1[one][three]]
                ):
                    return False
    return True


def right_distributive(table1: CayleyTable, table2: CayleyTable) -> bool:
    """
    >>> operation = {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "0"}}
    >>> right_distributive(operation, operation)
    True
    >>> operation = {"0": {"0": "0", "1": "1"}, "1": {"0": "0", "1": "0"}}
    >>> right_distributive(operation, operation)
    False

    :param table1: a multiplication table of a binary operation
    :param table2: a multiplication table of another binary operation
    :returns: whether the first operation is right distributive with respect to
        the second one or not
    """
    for one in table1.keys():
        for two in table1.keys():
            for three in table1.keys():
                if (
                    table1[table2[one][two]][three]
                    != table2[table1[one][three]][table1[two][three]]
                ):
                    return False
    return True


def absorbs(table1: CayleyTable, table2: CayleyTable) -> bool:
    """
    >>> conjuction = {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}}
    >>> disjunction = {"0": {"0": "0", "1": "1"}, "1": {"0": "1", "1": "1"}}
    >>> absorbs(conjuction, disjunction)
    True
    >>> absorbs(conjuction, conjuction)
    False

    :param table1: a multiplication table of a binary operation
    :param table2: a multiplication table of another binary operation
    :returns: whether the absorption law is true with respect to
        two binary operation
    """
    for one in table1.keys():
        for two in table1.keys():
            if table1[one][table2[one][two]] != one:
                return False
    return True


def is_left_zero(cayley_table: CayleyTable, zero: str) -> bool:
    """
    >>> table = {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}}
    >>> is_left_zero(table, "0")
    True
    >>> is_left_zero(table, "1")
    False

    :param cayley_table: a multiplication table of a binary operation
    :param zero: a symbol for the zero
    :returns: whether ``zero`` is a left zero for a Cayley table
    """
    for one in cayley_table.keys():
        if cayley_table[zero][one] != zero:
            return False
    return True


def is_right_zero(cayley_table: CayleyTable, zero: str) -> bool:
    """
    >>> table = {"0": {"0": "0", "1": "0"}, "1": {"0": "0", "1": "1"}}
    >>> is_right_zero(table, "0")
    True
    >>> is_right_zero(table, "1")
    False

    :param cayley_table: a multiplication table of a binary operation
    :param zero: a symbol for the zero
    :returns: whether ``zero`` is a right zero for a Cayley table
    """
    for one in cayley_table.keys():
        if cayley_table[one][zero] != zero:
            return False
    return True
