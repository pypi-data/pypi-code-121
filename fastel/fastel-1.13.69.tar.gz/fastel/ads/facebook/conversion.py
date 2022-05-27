import time
from typing import Any, Dict, List, Optional, Tuple

from facebook_business.adobjects.serverside.action_source import ActionSource
from facebook_business.adobjects.serverside.content import Content
from facebook_business.adobjects.serverside.custom_data import CustomData
from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.api import FacebookAdsApi
from pydantic import BaseModel

from fastel.config import SdkConfig


class UserForm(BaseModel):
    email: str
    phone: Optional[str]
    city: Optional[str]
    state: Optional[str]


class ItemForm(BaseModel):
    product_id: str
    quantity: int
    item_price: int
    title: str
    category: Optional[str]


class ItemsForm(BaseModel):
    order_id: Optional[str] = None
    price: Optional[int] = None
    content: List[ItemForm]


def user_parser(user_dict: Dict[str, Any]) -> UserForm:
    return UserForm(**user_dict)


def items_parser(items_dict: Dict[str, Any]) -> Tuple[UserForm, ItemsForm]:
    item_list = []
    user_dict = {
        "email": items_dict.get("buyer_email", "no-email@revtel-api.com"),
        "phone": items_dict["buyer_phone"],
        "city": items_dict["buyer_city"],
        "state": items_dict["buyer_district"],
    }
    user = UserForm(**user_dict)

    for item in items_dict["items"]:
        category = item["product"].get("labels", None)
        item_dict = {
            "product_id": item["product"]["id"]["$oid"],
            "quantity": item["config"]["qty"],
            "item_price": item["amount"],
            "title": item["name"],
            "category": category[0] if category else "no-cat",
        }
        item_list.append(item_dict)

    order_id = items_dict.get("order_id", None)
    items = ItemsForm(
        order_id=order_id, price=items_dict["subtotal"], content=item_list
    )
    return user, items


class ConversionApi:
    conversion_id: str = ""

    @classmethod
    def init(cls) -> Any:
        cls.conversion_id = SdkConfig.conversion_id
        FacebookAdsApi.init(access_token=SdkConfig.conversion_token)

    @classmethod
    def push_event(
        cls,
        action: str,
        user_model: UserForm,
        custom_model: Optional[ItemsForm] = None,
        raise_exception: bool = False,
    ) -> Any:
        try:
            user_data = UserData(**user_model.dict(exclude_none=True))

            custom_data = None
            if custom_model:
                contents = [
                    Content(**item.dict(exclude_none=True))
                    for item in custom_model.content
                ]
                custom_data = CustomData(
                    currency="twd",
                    order_id=custom_model.order_id,
                    value=custom_model.price,
                    contents=contents,
                )

            event = Event(
                event_name=action,
                event_time=int(time.time()),
                user_data=user_data,
                custom_data=custom_data,
                action_source=ActionSource.WEBSITE,
            )
            events = [event]
            event_request = EventRequest(
                events=events,
                pixel_id=cls.conversion_id,
            )
            event_result = event_request.execute()
            print("[SUCCESS]", event_result)
            return event_result

        except Exception as exc:
            print("[ERROR]", str(exc))
            if raise_exception:
                raise exc

    @classmethod
    def push_register_event(cls, user_dict: Dict[str, Any]) -> Any:
        if cls.conversion_id:
            user = user_parser(user_dict)
            cls.push_event("CompleteRegistration", user, None)

    @classmethod
    def push_add_cart_event(cls, cart_dict: Dict[str, Any]) -> Any:
        if cls.conversion_id:
            user, items = items_parser(cart_dict)
            cls.push_event("AddToCart", user, items)

    @classmethod
    def push_checkout_event(cls, checkout_dict: Dict[str, Any]) -> Any:
        if cls.conversion_id:
            user, items = items_parser(checkout_dict)
            cls.push_event("InitiateCheckout", user, items)

    @classmethod
    def push_purchase_event(cls, order_dict: Dict[str, Any]) -> Any:
        if cls.conversion_id:
            user, items = items_parser(order_dict)
            cls.push_event("Purchase", user, items)
