from dataclasses import dataclass, field
from typing import Dict, Optional, Union

from dataclasses_json import Undefined, config, dataclass_json


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Price:
    cents: int
    currency: str
    currency_symbol: str
    formatted: str


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Expansion:
    code: str
    id_: int = field(metadata=config(field_name="id"))
    name: str = field(metadata=config(field_name="name_en"))


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class User:
    can_sell_sealed_with_ct_zero: bool
    can_sell_via_hub: bool
    country_code: str
    id_: int = field(metadata=config(field_name="id"))
    too_many_request_for_cancel_as_seller: bool
    user_type: str
    username: str
    max_sellable_in24h_quantity: Optional[int] = None


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Product:
    blueprint_id: int
    bundle_size: int
    expansion: Expansion
    id_: int = field(metadata=config(field_name="id"))
    name: str = field(metadata=config(field_name="name_en"))
    on_vacation: bool
    price: Price
    price_cents: int
    price_currency: str
    quantity: int
    seller: User = field(metadata=config(field_name="user"))
    description: Optional[str] = None
    graded: Optional[bool] = None
    layered_price_cents: Optional[int] = None
    properties: Dict[str, Optional[Union[str, bool]]] = field(
        default_factory=dict, metadata=config(field_name="properties_hash")
    )
    tag: Optional[str] = None
