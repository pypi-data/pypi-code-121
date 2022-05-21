from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

import attr

from ..models.billing_price import BillingPrice
from ..types import UNSET
from ..util.serialization import is_not_none

T = TypeVar("T", bound="EventBillingPriceUpdate")


@attr.s(auto_attribs=True)
class EventBillingPriceUpdate:
    """
    Attributes:
        billing_price (BillingPrice): The price schedule for a particular service applied to an invoice line item.
    """

    billing_price: BillingPrice
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self, pick_by_predicate: Optional[Callable[[Any], bool]] = is_not_none) -> Dict[str, Any]:
        billing_price = self.billing_price.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "billingPrice": billing_price,
            }
        )

        field_dict = {k: v for k, v in field_dict.items() if v != UNSET}
        if pick_by_predicate is not None:
            field_dict = {k: v for k, v in field_dict.items() if pick_by_predicate(v)}

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        billing_price = BillingPrice.from_dict(d.pop("billingPrice"))

        event_billing_price_update = cls(
            billing_price=billing_price,
        )

        event_billing_price_update.additional_properties = d
        return event_billing_price_update

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
