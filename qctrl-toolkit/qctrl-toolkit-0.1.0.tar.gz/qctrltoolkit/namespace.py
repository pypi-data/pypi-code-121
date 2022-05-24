# Copyright 2022 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""
Namespaces for the toolkit functions, nodes, and classes.

These namespaces are categorized by physical system.
"""

from collections import namedtuple
from enum import Enum

_SUPERCONDUCTING_DOC = """
    Toolkit for superconducting qubits.
"""


_IONS_DOC = """
    Toolkit for trapped ions.
"""

_UTILS_DOC = """
    Toolkit for system-agnostic functionality.
"""

_NamespaceItem = namedtuple("_NamespaceItem", ["name", "doc"])


class Namespace(Enum):
    """
    An enumeration of namespaces defined by physical systems.

    The `UTILS` namespace holds system-independent functionality.
    """

    SUPERCONDUCTING = _NamespaceItem("superconducting", _SUPERCONDUCTING_DOC)
    IONS = _NamespaceItem("ions", _IONS_DOC)
    UTILS = _NamespaceItem("utils", _UTILS_DOC)

    def get_name(self):
        """
        Get the name of the namespace.
        """
        return self.value.name

    def get_doc(self):
        """
        Get the doc of the namespace.
        """
        return self.value.doc
