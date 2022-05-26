from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Iterable, Optional, TypeVar

from sila2.client.polling_subscription import PollingSubscription
from sila2.client.subscription import Subscription
from sila2.client.utils import call_rpc_function
from sila2.framework.property.unobservable_property import UnobservableProperty

if TYPE_CHECKING:
    from sila2.client.client_feature import ClientFeature
    from sila2.client.client_metadata import ClientMetadataInstance

ItemType = TypeVar("ItemType")


class ClientUnobservableProperty(Generic[ItemType]):
    """Wraps an unobservable property"""

    def __init__(self, parent_feature: ClientFeature, wrapped_property: UnobservableProperty):
        self._parent_feature = parent_feature
        self._wrapped_property = wrapped_property

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
        """
        param_msg = self._wrapped_property.get_parameters_message()

        response_msg = call_rpc_function(
            getattr(self._parent_feature._grpc_stub, f"Get_{self._wrapped_property._identifier}"),
            param_msg,
            metadata=metadata,
            client=self._parent_feature._parent_client,
            origin=self._wrapped_property,
        )

        return self._wrapped_property.to_native_type(response_msg)

    def subscribe_by_polling(
        self, poll_interval: float, *, metadata: Optional[Iterable[ClientMetadataInstance]] = None
    ) -> Subscription[ItemType]:
        """
        Subscribe to value updates by repeatedly calling ``get()`` in a background thread.

        Parameters
        ----------
        poll_interval
            Time in seconds between calling ``get()``
        metadata
            SiLA Client Metadata to send along with the subscription request
        Returns
        -------
        subscription
            Property value subscription

        Notes
        -----
        When receiving the same value multiple times in a row, it is only emitted once.
        This simulates the subscription behavior of observable properties,
        which can be used to "observe any change of its value".
        """
        return PollingSubscription(
            lambda: self.get(metadata=metadata), self._parent_feature._parent_client._task_executor, poll_interval
        )
