from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Iterable, Optional, TypeVar

from sila2.client.grpc_stream_subscription import GrpcStreamSubscription
from sila2.client.subscription import Subscription
from sila2.client.utils import call_rpc_function
from sila2.framework.property.observable_property import ObservableProperty

if TYPE_CHECKING:
    from sila2.client.client_feature import ClientFeature
    from sila2.client.client_metadata import ClientMetadataInstance

ItemType = TypeVar("ItemType")


class ClientObservableProperty(Generic[ItemType]):
    """Wraps an observable property"""

    def __init__(self, parent_feature: ClientFeature, wrapped_property: ObservableProperty):
        self._parent_feature = parent_feature
        self._wrapped_property = wrapped_property

    def subscribe(self, *, metadata: Optional[Iterable[ClientMetadataInstance]] = None) -> Subscription[ItemType]:
        """
        Subscribe to value updates

        Parameters
        ----------
        metadata
            SiLA Client Metadata to send along with the subscription request
        Returns
        -------
        subscription
            Property value subscription
        """
        param_msg = self._wrapped_property.get_parameters_message()
        rpc_func = getattr(self._parent_feature._grpc_stub, f"Subscribe_{self._wrapped_property._identifier}")
        response_stream = call_rpc_function(
            rpc_func,
            param_msg,
            metadata=metadata,
            client=self._parent_feature._parent_client,
            origin=self._wrapped_property,
        )
        return GrpcStreamSubscription(
            response_stream, self._wrapped_property.to_native_type, self._parent_feature._parent_client._task_executor
        )

    def get(self, *, metadata: Optional[Iterable[ClientMetadataInstance]] = None) -> ItemType:
        """
        Get the current value

        Parameters
        ----------
        metadata
            SiLA Client Metadata to send along with the subscription request

        Returns
        -------
        value
            Current property value

        Notes
        -----
        This is equivalent to subscribing to the property and cancelling the subscription after receiving the first
        item
        """
        with self.subscribe(metadata=metadata) as sub:
            return next(sub)
