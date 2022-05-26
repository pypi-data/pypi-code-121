from __future__ import annotations

from typing import TYPE_CHECKING, List

from sila2.framework.abc.composite_message_mappable import CompositeMessageMappable
from sila2.framework.abc.named_node import NamedNode
from sila2.framework.command.parameter import Parameter
from sila2.framework.command.response import Response
from sila2.framework.defined_execution_error_node import DefinedExecutionErrorNode
from sila2.framework.fully_qualified_identifier import FullyQualifiedCommandIdentifier
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


class Command(NamedNode):
    """Represents a command"""

    fully_qualified_identifier: FullyQualifiedCommandIdentifier
    """Fully qualified command identifier"""
    parent_feature: Feature
    parameters: CompositeMessageMappable[Parameter]
    responses: CompositeMessageMappable[Response]
    defined_execution_errors: List[DefinedExecutionErrorNode]

    def __init__(self, fdl_node, parent_feature: Feature):
        super().__init__(fdl_node)
        self.parent_feature = parent_feature
        self.fully_qualified_identifier = FullyQualifiedCommandIdentifier(
            f"{parent_feature.fully_qualified_identifier}/Command/{self._identifier}"
        )
        self.parameters = CompositeMessageMappable(
            [Parameter(node, self) for node in xpath_sila(fdl_node, "sila:Parameter")],
            getattr(self.parent_feature._pb2_module, f"{self._identifier}_Parameters"),
        )
        self.responses = CompositeMessageMappable(
            [Response(node, self) for node in xpath_sila(fdl_node, "sila:Response")],
            getattr(self.parent_feature._pb2_module, f"{self._identifier}_Responses"),
        )
        self.defined_execution_errors = [
            parent_feature.defined_execution_errors[name]
            for name in xpath_sila(fdl_node, "sila:DefinedExecutionErrors/sila:Identifier/text()")
        ]

    @staticmethod
    def from_fdl_node(fdl_node, parent_feature: Feature) -> Command:
        if xpath_sila(fdl_node, "sila:Observable/text() = 'No'"):
            from sila2.framework.command.unobservable_command import UnobservableCommand

            return UnobservableCommand(fdl_node, parent_feature)
        from sila2.framework.command.observable_command import ObservableCommand

        return ObservableCommand(fdl_node, parent_feature)
