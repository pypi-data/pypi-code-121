from __future__ import annotations

from typing import TYPE_CHECKING

from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.fully_qualified_identifier import FullyQualifiedCommandParameterIdentifier

if TYPE_CHECKING:
    from sila2.framework.command.command import Command


class Parameter(NamedDataNode):
    """Represents a command parameter"""

    fully_qualified_identifier: FullyQualifiedCommandParameterIdentifier
    """Fully qualified parameter identifier"""
    parent_command: Command

    def __init__(self, fdl_node, parent_command: Command):
        super().__init__(
            fdl_node,
            parent_command.parent_feature,
            getattr(parent_command.parent_feature._pb2_module, f"{parent_command._identifier}_Parameters"),
        )
        self.fully_qualified_identifier = FullyQualifiedCommandParameterIdentifier(
            f"{parent_command.fully_qualified_identifier}/Parameter/{self._identifier}"
        )
