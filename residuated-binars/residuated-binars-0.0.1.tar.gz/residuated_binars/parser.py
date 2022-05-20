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
Parser
=======
"""
import json
import re
from typing import Any, Dict, List, Union

from residuated_binars.algebraic_structure import (
    AlgebraicStructure,
    CayleyTable,
)
from residuated_binars.lattice import Lattice
from residuated_binars.residuated_binar import ResiduatedBinar


def parse_binary_operation(line: str) -> CayleyTable:
    """
    parse text describing a binary operation in Isabelle server response

    :param line: a part of Isabelle server response, representing a binary
        operation
    :returns: a Cayley table
    """
    table: CayleyTable = {}
    regex = re.compile(
        r"\(([\w\\\^\<\>]+), ([\w\\\^\<\>]+)\) := ([\w\\\^\<\>]+)"
    )
    match = regex.search(line)
    while match is not None:
        pos = match.span()[-1] + 1
        args = list(match.groups())
        if args[0] not in table:
            table[args[0]] = {}
        table[args[0]][args[1]] = args[2]
        match = regex.search(line, pos)
    return table


def parse_unary_operation(line: str) -> Dict[str, str]:
    """
    parse text describing a unary operation in Isabelle server response

    :param line: a part of Isabelle server response, representing an unary
        operation
    :returns: an inner representation of an unary operation
    """
    table: Dict[str, str] = {}
    regex = re.compile(r"([\w\\\<\>\^]+) := ([\w\\\<\>\^]+)")
    match = regex.search(line)
    while match is not None:
        pos = match.span()[-1] + 1
        args = list(match.groups())
        table[args[0]] = args[1]
        match = regex.search(line, pos)
    return table


def choose_algebraic_structure(
    label: str, operations: Dict[str, Dict[str, Any]]
) -> AlgebraicStructure:
    """
    :param label: a name of that particular algebraic structure example
    :param operations: a dictionary of unary and binary operations
    :returns: an algebraic structure of a concrete type (
        depending on the signature)
    """
    sorted_ops = sorted(operations.keys())
    if sorted_ops == ["join", "meet"]:
        return Lattice(label, operations)
    if sorted_ops in [
        [
            "join",
            "meet",
            "mult",
            "over",
            "undr",
        ],
        ["invo", "join", "meet", "mult", "over", "undr"],
    ]:
        return ResiduatedBinar(label, operations)
    return AlgebraicStructure(label, operations)


def isabelle_format_to_algebra(
    isabelle_message: str, label: str
) -> AlgebraicStructure:
    """
    :param isabelle_message: a body of reply from Isabelle server (in JSON)
    :param label: a name of the theory for which we got a relply from server
    :returns: a residuated binar
    """
    regex = re.compile(
        r"    (\w+) =\n? +\(\\<lambda>x\. _\)\n? *\(([^\.]+)\)\n?",
        re.DOTALL,
    )
    match = regex.search(isabelle_message)
    operations: Dict[str, Union[CayleyTable, Dict[str, str]]] = {}
    while match is not None:
        table: Union[CayleyTable, Dict[str, str]] = parse_binary_operation(
            match.group(2)
        )
        if not table:
            table = parse_unary_operation(match.group(2))
        operations[match.group(1)] = table
        pos = match.span()[0] + 1
        match = regex.search(isabelle_message, pos)
    return choose_algebraic_structure(label, operations)


def isabelle_response_to_algebra(filename: str) -> List[AlgebraicStructure]:
    """
    read file with replies from ``isabelle`` server and parse all residuated
    binars from it

    >>> import sys
    >>> if sys.version_info.major == 3 and sys.version_info.minor >= 9:
    ...     from importlib.resources import files
    ... else:
    ...     from importlib_resources import files
    >>> import os
    >>> len(isabelle_response_to_algebra(
    ...     files("residuated_binars")
    ...     .joinpath(os.path.join("resources", "isabelle2.out"))
    ... ))
    6

    :param filename: a name of a file to which all replies from Isabelle server
        where written
    :returns: a list of algebraic structures
    """
    with open(filename, "r", encoding="utf-8") as isabelle_log:
        nodes = json.loads(
            [
                line
                for line in isabelle_log.readlines()
                if "FINISHED" in line and "lambda" in line
            ][0][9:]
        )["nodes"]
    messages = [
        (
            [
                message["message"]
                for message in node["messages"]
                if "lambda" in message["message"]
            ][:1],
            node["theory_name"].split(".")[1],
        )
        for node in nodes
    ]
    return [
        isabelle_format_to_algebra(message[0][0], message[1])
        for message in messages
        if message[0] != []
    ]
