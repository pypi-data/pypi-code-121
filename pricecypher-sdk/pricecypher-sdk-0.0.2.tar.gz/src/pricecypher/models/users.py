from dataclasses import field
from datetime import datetime
from typing import Optional
from marshmallow_dataclass import dataclass

from pricecypher.models.namespaced_schema import NamespacedSchema


@dataclass(base_schema=NamespacedSchema, frozen=True)
class Dataset:
    id: int = field(compare=True)
    name: str = field(compare=False)
    dss_url: Optional[str] = field(compare=False)
    created_at: datetime = field(compare=False)
    updated_at: datetime = field(compare=False)
    modules: list[str] = field(compare=False)

    class Meta:
        name = "dataset"
        plural_name = "datasets"
