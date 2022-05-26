from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Iterable, NamedTuple, Optional, TypeVar

from sila2.client.client_metadata import ClientMetadataInstance
from sila2.client.utils import call_rpc_function
from sila2.framework.command.unobservable_command import UnobservableCommand

if TYPE_CHECKING:
    from sila2.client.client_feature import ClientFeature

ResponseType = TypeVar("ResponseType", bound=NamedTuple)


class ClientUnobservableCommand(Generic[ResponseType]):
    """
    Wraps an unobservable command
    """

    def __init__(self, parent_feature: ClientFeature, wrapped_command: UnobservableCommand):
        self._parent_feature = parent_feature
        self._wrapped_command = wrapped_command

    def __call__(self, *args, **kwargs) -> ResponseType:
        """
        Request execution of the unobservable command

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
        responses
            Command responses as named tuple
        """
        raw_metadata: Optional[Iterable[ClientMetadataInstance]] = kwargs.pop("metadata", None)
        param_msg = self._wrapped_command.parameters.to_message(
            *args, **kwargs, toplevel_named_data_node=self._wrapped_command.parameters
        )
        response_msg = call_rpc_function(
            getattr(self._parent_feature._grpc_stub, self._wrapped_command._identifier),
            param_msg,
            metadata=raw_metadata,
            client=self._parent_feature._parent_client,
            origin=self._wrapped_command,
        )

        return self._wrapped_command.responses.to_native_type(response_msg)
