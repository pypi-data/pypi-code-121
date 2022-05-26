from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .EntityHelper import EntityHelper

Entity = TypeVar["net.minecraft.entity.Entity"]

class EventEntityDamaged(BaseEvent):
	entity: EntityHelper
	health: float
	damage: float

	@overload
	def __init__(self, e: Entity, health: float, amount: float) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


