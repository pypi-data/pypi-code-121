from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..models.event_billing_price import EventBillingPrice
from ..types import UNSET, Unset
from ..util.serialization import is_not_none

T = TypeVar("T", bound="ListEventBillingPricesResponse")


@attr.s(auto_attribs=True)
class ListEventBillingPricesResponse:
    """
    Attributes:
        event_billing_prices (List[EventBillingPrice]):
        next_page_token (Union[Unset, str]):
    """

    event_billing_prices: List[EventBillingPrice]
    next_page_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self, pick_by_predicate: Optional[Callable[[Any], bool]] = is_not_none) -> Dict[str, Any]:
        event_billing_prices = []
        for event_billing_prices_item_data in self.event_billing_prices:
            event_billing_prices_item = event_billing_prices_item_data.to_dict()

            event_billing_prices.append(event_billing_prices_item)

        next_page_token = self.next_page_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "eventBillingPrices": event_billing_prices,
            }
        )
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        field_dict = {k: v for k, v in field_dict.items() if v != UNSET}
        if pick_by_predicate is not None:
            field_dict = {k: v for k, v in field_dict.items() if pick_by_predicate(v)}

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        event_billing_prices = []
        _event_billing_prices = d.pop("eventBillingPrices")
        for event_billing_prices_item_data in _event_billing_prices:
            event_billing_prices_item = EventBillingPrice.from_dict(event_billing_prices_item_data)

            event_billing_prices.append(event_billing_prices_item)

        next_page_token = d.pop("nextPageToken", UNSET)

        list_event_billing_prices_response = cls(
            event_billing_prices=event_billing_prices,
            next_page_token=next_page_token,
        )

        list_event_billing_prices_response.additional_properties = d
        return list_event_billing_prices_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
