from __future__ import annotations

from typing import TYPE_CHECKING

from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.fully_qualified_identifier import FullyQualifiedIntermediateCommandResponseIdentifier

if TYPE_CHECKING:
    from sila2.framework.command.command import Command


class IntermediateResponse(NamedDataNode):
    """Represents a command intermediate response"""

    fully_qualified_identifier: FullyQualifiedIntermediateCommandResponseIdentifier
    """Fully qualified intermediate response identifier"""
    parent_command: Command

    def __init__(self, fdl_node, parent_command: Command):
        super().__init__(
            fdl_node,
            parent_command.parent_feature,
            getattr(parent_command.parent_feature._pb2_module, f"{parent_command._identifier}_IntermediateResponses"),
        )
        self.fully_qualified_identifier = FullyQualifiedIntermediateCommandResponseIdentifier(
            f"{parent_command.fully_qualified_identifier}/IntermediateResponse/{self._identifier}"
        )
