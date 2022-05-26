from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, List, TypeVar

from sila2.client.utils import call_rpc_function
from sila2.framework.fully_qualified_identifier import FullyQualifiedIdentifier
from sila2.framework.metadata import Metadata
from sila2.framework.pb2.custom_protocols import AffectedCallsMessage

if TYPE_CHECKING:
    from sila2.client.client_feature import ClientFeature

ItemType = TypeVar("ItemType")


@dataclass
class ClientMetadataInstance(Generic[ItemType]):
    """Pair of metadata type and value, like a key-value pair"""

    metadata: Metadata
    """Metadata type"""
    value: ItemType
    """Metadata value"""


class ClientMetadata(Generic[ItemType]):
    """Wraps a metadata element"""

    def __init__(self, parent_feature: ClientFeature, wrapped_metadata: Metadata):
        self._parent_feature = parent_feature
        self._wrapped_metadata = wrapped_metadata
        self.fully_qualified_identifier = self._wrapped_metadata.fully_qualified_identifier

    def __call__(self, value: ItemType) -> ClientMetadataInstance[ItemType]:
        """
        Create an instance of this metadata with the given value

        Parameters
        ----------
        value
            The metadata value

        Returns
        -------
        instance
            An instance of this metadata with the given value
        """
        return ClientMetadataInstance(self._wrapped_metadata, value)

    def get_affected_calls(self) -> List[FullyQualifiedIdentifier]:
        """
        Get the list of calls that are affected by this metadata

        Returns
        -------
        affected_calls
            List of fully qualified identifiers of features, commands, and properties that are affected by this metadata
        """
        param_msg = self._wrapped_metadata.get_affected_calls_parameters_message()

        response_msg: AffectedCallsMessage = call_rpc_function(
            getattr(self._parent_feature._grpc_stub, f"Get_FCPAffectedByMetadata_{self._wrapped_metadata._identifier}"),
            param_msg,
            metadata=None,
            client=self._parent_feature._parent_client,
            origin=None,
        )

        return [
            FullyQualifiedIdentifier(identifier_sila_string.value)
            for identifier_sila_string in response_msg.AffectedCalls
        ]
