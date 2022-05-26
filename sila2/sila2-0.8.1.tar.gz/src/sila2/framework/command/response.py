from __future__ import annotations

from typing import TYPE_CHECKING

from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.fully_qualified_identifier import FullyQualifiedCommandResponseIdentifier

if TYPE_CHECKING:
    from sila2.framework.command.command import Command


class Response(NamedDataNode):
    """Represents a command response"""

    fully_qualified_identifier: FullyQualifiedCommandResponseIdentifier
    """Fully qualified response identifier"""
    parent_command: Command

    def __init__(self, fdl_node, parent_command: Command):
        super().__init__(
            fdl_node,
            parent_command.parent_feature,
            getattr(parent_command.parent_feature._pb2_module, f"{parent_command._identifier}_Responses"),
        )
        self.fully_qualified_identifier = FullyQualifiedCommandResponseIdentifier(
            f"{parent_command.fully_qualified_identifier}/Response/{self._identifier}"
        )
