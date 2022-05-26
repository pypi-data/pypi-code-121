from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Union

from sila2.client.client_metadata import ClientMetadata
from sila2.client.client_observable_command import ClientObservableCommand
from sila2.client.client_observable_property import ClientObservableProperty
from sila2.client.client_unobservable_command import ClientUnobservableCommand
from sila2.client.client_unobservable_property import ClientUnobservableProperty
from sila2.framework.binary_transfer.client_binary_transfer_handler import ClientBinaryTransferHandler
from sila2.framework.feature import Feature

if TYPE_CHECKING:
    from sila2.client.sila_client import SilaClient

GrpcStub = Any


class ClientFeature(Feature):
    _grpc_stub: GrpcStub
    _parent_client: SilaClient
    _binary_transfer_handler: ClientBinaryTransferHandler
    _client_commands: Dict[str, Union[ClientUnobservableCommand, ClientObservableCommand]]
    _client_properties: Dict[str, Union[ClientUnobservableProperty, ClientObservableProperty]]
    _client_metadata: Dict[str, ClientMetadata]

    def __init__(self, feature_definition: str, parent_client: SilaClient):
        super().__init__(feature_definition)
        self._parent_client = parent_client
        self._grpc_stub = getattr(self._grpc_module, f"{self._identifier}Stub")(parent_client._channel)
        self._binary_transfer_handler = ClientBinaryTransferHandler(parent_client._channel)

        self._client_properties = {}
        self._client_commands = {}
        self._client_metadata = {}
        for identifier, prop in self._unobservable_properties.items():
            client_prop = ClientUnobservableProperty(self, prop)
            self._client_properties[identifier] = client_prop
            setattr(self, identifier, client_prop)
        for identifier, prop in self._observable_properties.items():
            client_prop = ClientObservableProperty(self, prop)
            self._client_properties[identifier] = client_prop
            setattr(self, identifier, ClientObservableProperty(self, prop))
        for identifier, cmd in self._unobservable_commands.items():
            client_cmd = ClientUnobservableCommand(self, cmd)
            self._client_commands[identifier] = client_cmd
            setattr(self, identifier, client_cmd)
        for identifier, cmd in self._observable_commands.items():
            client_cmd = ClientObservableCommand(self, cmd)
            self._client_commands[identifier] = client_cmd
            setattr(self, identifier, client_cmd)
        for identifier, meta in self.metadata_definitions.items():
            client_metadata = ClientMetadata(self, meta)
            self._client_metadata[identifier] = client_metadata
            setattr(self, identifier, client_metadata)
