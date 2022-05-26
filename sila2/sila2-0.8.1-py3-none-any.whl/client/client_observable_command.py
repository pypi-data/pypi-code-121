from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Iterable, Optional, TypeVar

from sila2.client.client_metadata import ClientMetadataInstance
from sila2.client.client_observable_command_instance import (
    ClientObservableCommandInstance,
    ClientObservableCommandInstanceWithIntermediateResponses,
)
from sila2.client.utils import call_rpc_function
from sila2.framework.command.command_confirmation import CommandConfirmation
from sila2.framework.command.observable_command import ObservableCommand

if TYPE_CHECKING:
    from sila2.client.client_feature import ClientFeature
    from sila2.framework.pb2.SiLAFramework_pb2 import CommandConfirmation as SilaCommandConfirmation

ResultType = TypeVar("ResultType")
IntermediateType = TypeVar("IntermediateType")


class ClientObservableCommand(Generic[ResultType, IntermediateType]):
    """
    Wraps an observable command
    """

    def __init__(self, parent_feature: ClientFeature, wrapped_command: ObservableCommand):
        self._parent_feature: ClientFeature = parent_feature
        self._wrapped_command: ObservableCommand = wrapped_command

    def __call__(self, *args, **kwargs) -> ClientObservableCommandInstance:
        """
        Request execution of the observable command

        Parameters
        ----------
        args
            Command parameters as positional arguments
        kwargs
            Command parameters as keyword arguments
        metadata: Optional[Iterable[ClientMetadataInstance]]
            SiLA Client Metadata to send along with the request

        Returns
        -------
        instance
            Instance of the command execution
        """
        raw_metadata: Optional[Iterable[ClientMetadataInstance]] = kwargs.pop("metadata", None)
        param_msg = self._wrapped_command.parameters.to_message(*args, **kwargs)
        response_msg: SilaCommandConfirmation = call_rpc_function(
            getattr(self._parent_feature._grpc_stub, self._wrapped_command._identifier),
            param_msg,
            metadata=raw_metadata,
            client=self._parent_feature._parent_client,
            origin=self._wrapped_command,
        )
        exec_id, lifetime = CommandConfirmation(self._parent_feature._pb2_module.SiLAFramework__pb2).to_native_type(
            response_msg
        )
        if self._wrapped_command.intermediate_responses:
            return ClientObservableCommandInstanceWithIntermediateResponses(
                self._parent_feature._parent_client, self, exec_id, lifetime
            )
        return ClientObservableCommandInstance(self._parent_feature._parent_client, self, exec_id, lifetime)
