from dataclasses import field
from datetime import datetime
from typing import Optional, List, Union
from marshmallow_dataclass import dataclass

from pricecypher.models.namespaced_schema import NamespacedSchema


@dataclass(base_schema=NamespacedSchema, frozen=True)
class Scope:
    id: int = field(compare=True)
    data_version_id: int = field(compare=False)
    order: Optional[int] = field(compare=False)
    type: str = field(compare=False)
    representation: Optional[str] = field(compare=False)
    name_dataset: str = field(compare=False)
    name_human: Optional[str] = field(compare=False)
    multiply_by_volume_enabled: bool = field(compare=False)
    default_aggregation_method: Optional[str] = field(compare=False)

    class Meta:
        name = "scope"
        plural_name = "scopes"


@dataclass(base_schema=NamespacedSchema, frozen=True)
class ScopeValue:
    id: str = field(compare=True)
    scope_id: int = field(compare=False)
    value: str = field(compare=False)

    class Meta:
        name = "scope_value"
        plural_name = "scope_values"


@dataclass(base_schema=NamespacedSchema, frozen=True)
class TransactionSummary:
    first_date_time: datetime = field(metadata=dict(data_key='first_date'))
    last_date_time: datetime = field(metadata=dict(data_key='last_date'))

    class Meta:
        name = "summary"
        plural_name = "summaries"


@dataclass(frozen=True)
class ScopeValueTransaction:
    scope_id: int
    value: Optional[str]


@dataclass(frozen=True)
class ScopeConstantTransaction:
    scope_id: int
    constant: Union[str, float, None]


@dataclass(base_schema=NamespacedSchema, frozen=True)
class Transaction:
    id: Optional[int]
    external_id: Optional[str]
    count: Optional[int]
    volume: float
    price: float
    date_time: datetime
    currency: str
    unit: Optional[str]
    scope_values: List[ScopeValueTransaction]
    scope_constants: List[ScopeConstantTransaction]

    class Meta:
        name = "transaction"
        plural_name = "transactions"

    def to_dict(self, scope_keys):
        dic = {
            'id': self.id,
            'external_id': self.external_id,
            'count': self.count,
            'volume': self.volume,
            'price': self.price,
            'date_time': self.date_time,
            'currency': self.currency,
            'unit': self.unit,
        }

        for scope_value in self.scope_values:
            if scope_value.scope_id in scope_keys:
                scope_key = scope_keys[scope_value.scope_id]
                dic[scope_key] = scope_value.value

        for scope_constant in self.scope_constants:
            if scope_constant.scope_id in scope_keys:
                scope_key = scope_keys[scope_constant.scope_id]
                dic[scope_key] = scope_constant.constant

        return dic

