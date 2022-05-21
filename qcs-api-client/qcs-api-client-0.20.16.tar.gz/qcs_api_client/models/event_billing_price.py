import datetime
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse
from rfc3339 import rfc3339

from ..models.account_type import AccountType
from ..models.billing_price import BillingPrice
from ..models.event_billing_price_product import EventBillingPriceProduct
from ..types import UNSET, Unset
from ..util.serialization import is_not_none

T = TypeVar("T", bound="EventBillingPrice")


@attr.s(auto_attribs=True)
class EventBillingPrice:
    """Event price. Maps billing account, event, and quantum processor identifier (we refer to this as an event scope) to a
    price identifier.

        Attributes:
            billing_price (BillingPrice): The price schedule for a particular service applied to an invoice line item.
            created_time (datetime.datetime):
            creator_id (str):
            id (int):
            product (EventBillingPriceProduct):
            account_id (Union[Unset, str]): userId for `accountType` "user", group name for `accountType` "group".
            account_type (Union[Unset, AccountType]): There are two types of accounts within QCS: user (representing a
                single user in Okta) and group
                (representing one or more users in Okta).
            deleted (Union[Unset, Any]): Metadata for resources that are soft deleted.
            quantum_processor_id (Union[Unset, str]):
    """

    billing_price: BillingPrice
    created_time: datetime.datetime
    creator_id: str
    id: int
    product: EventBillingPriceProduct
    account_id: Union[Unset, str] = UNSET
    account_type: Union[Unset, AccountType] = UNSET
    deleted: Union[Unset, Any] = UNSET
    quantum_processor_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self, pick_by_predicate: Optional[Callable[[Any], bool]] = is_not_none) -> Dict[str, Any]:
        billing_price = self.billing_price.to_dict()

        assert self.created_time.tzinfo is not None, "Datetime must have timezone information"
        created_time = rfc3339(self.created_time)

        creator_id = self.creator_id
        id = self.id
        product = self.product.value

        account_id = self.account_id
        account_type: Union[Unset, str] = UNSET
        if not isinstance(self.account_type, Unset):
            account_type = self.account_type.value

        deleted = self.deleted
        quantum_processor_id = self.quantum_processor_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "billingPrice": billing_price,
                "createdTime": created_time,
                "creatorId": creator_id,
                "id": id,
                "product": product,
            }
        )
        if account_id is not UNSET:
            field_dict["accountId"] = account_id
        if account_type is not UNSET:
            field_dict["accountType"] = account_type
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if quantum_processor_id is not UNSET:
            field_dict["quantumProcessorId"] = quantum_processor_id

        field_dict = {k: v for k, v in field_dict.items() if v != UNSET}
        if pick_by_predicate is not None:
            field_dict = {k: v for k, v in field_dict.items() if pick_by_predicate(v)}

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        billing_price = BillingPrice.from_dict(d.pop("billingPrice"))

        created_time = isoparse(d.pop("createdTime"))

        creator_id = d.pop("creatorId")

        id = d.pop("id")

        product = EventBillingPriceProduct(d.pop("product"))

        account_id = d.pop("accountId", UNSET)

        _account_type = d.pop("accountType", UNSET)
        account_type: Union[Unset, AccountType]
        if isinstance(_account_type, Unset):
            account_type = UNSET
        else:
            account_type = AccountType(_account_type)

        deleted = d.pop("deleted", UNSET)

        quantum_processor_id = d.pop("quantumProcessorId", UNSET)

        event_billing_price = cls(
            billing_price=billing_price,
            created_time=created_time,
            creator_id=creator_id,
            id=id,
            product=product,
            account_id=account_id,
            account_type=account_type,
            deleted=deleted,
            quantum_processor_id=quantum_processor_id,
        )

        event_billing_price.additional_properties = d
        return event_billing_price

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
