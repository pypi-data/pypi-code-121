from dataclasses import dataclass, field
from typing import Any

from typing_extensions import Self, dataclass_transform


@dataclass_transform(
    eq_default=False,
    order_default=False,
    kw_only_default=True,
    field_descriptors=(field,),
)
class EntityMeta(type):
    def __new__(
        cls: type[Self], name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ) -> Self:
        new_cls = super().__new__(cls, name, bases, namespace)
        return dataclass(eq=False, kw_only=True)(new_cls)  # type: ignore


class Entity(metaclass=EntityMeta):
    ...
