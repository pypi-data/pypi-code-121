from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset
from ..util.serialization import is_not_none

T = TypeVar("T", bound="AccountBillingCustomerCreateRequest")


@attr.s(auto_attribs=True)
class AccountBillingCustomerCreateRequest:
    """If `id` is present, this will set the billing customer id to the requested account if the billing customer exists
    and has not been assigned to any other QCS account. Otherwise, it will create a new billing customer. In either
    case, it will ensure the billing customer has the appropriate metadata. Because QCS does not support updating
    billing customer data, `email` should only be set when `id` is not set.

        Attributes:
            email (Union[Unset, str]):
            id (Union[Unset, str]):
    """

    email: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self, pick_by_predicate: Optional[Callable[[Any], bool]] = is_not_none) -> Dict[str, Any]:
        email = self.email
        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if id is not UNSET:
            field_dict["id"] = id

        field_dict = {k: v for k, v in field_dict.items() if v != UNSET}
        if pick_by_predicate is not None:
            field_dict = {k: v for k, v in field_dict.items() if pick_by_predicate(v)}

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        email = d.pop("email", UNSET)

        id = d.pop("id", UNSET)

        account_billing_customer_create_request = cls(
            email=email,
            id=id,
        )

        account_billing_customer_create_request.additional_properties = d
        return account_billing_customer_create_request

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
