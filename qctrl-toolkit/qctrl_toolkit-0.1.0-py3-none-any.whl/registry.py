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
Registry for toolkits.
"""
import inspect

import qctrltoolkit.superconducting.node
import qctrltoolkit.superconducting.workflow
import qctrltoolkit.utils.node
import qctrltoolkit.utils.workflow
from qctrltoolkit.toolkit_utils import TOOLKIT_ATTR


def _register(modules):
    """
    Collect exposed toolkits from modules.
    """
    registered = []
    for module in modules:
        for _, member in inspect.getmembers(module):
            if hasattr(member, TOOLKIT_ATTR):
                registered.append(member)
    return registered


NODES = _register(
    [
        qctrltoolkit.superconducting.node,
        qctrltoolkit.utils.node,
    ]
)
WORKFLOWS = _register(
    [
        qctrltoolkit.superconducting.workflow,
        qctrltoolkit.utils.workflow,
    ]
)
