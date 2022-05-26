from typing import Generic, Optional, TypeVar

from sila2.framework.abc.composite_message_mappable import CompositeMessageMappable
from sila2.framework.command.command import Command
from sila2.framework.command.intermediate_response import IntermediateResponse
from sila2.framework.utils import xpath_sila

ParametersNamedTuple = TypeVar("ParametersNamedTuple")
IntermediateResponsesNamedTuple = TypeVar("IntermediateResponsesNamedTuple")
ResponsesNamedTuple = TypeVar("ResponsesNamedTuple")


class ObservableCommand(Command, Generic[ParametersNamedTuple, IntermediateResponsesNamedTuple, ResponsesNamedTuple]):
    """Represents an observable command"""

    intermediate_responses: Optional[CompositeMessageMappable[IntermediateResponse]]

    def __init__(self, fdl_node, parent_feature):
        super().__init__(fdl_node, parent_feature)
        intermediate_response_nodes = xpath_sila(fdl_node, "sila:IntermediateResponse")
        if intermediate_response_nodes:
            self.intermediate_responses = CompositeMessageMappable(
                [IntermediateResponse(node, self) for node in intermediate_response_nodes],
                getattr(self.parent_feature._pb2_module, f"{self._identifier}_IntermediateResponses"),
            )
        else:
            self.intermediate_responses = None
