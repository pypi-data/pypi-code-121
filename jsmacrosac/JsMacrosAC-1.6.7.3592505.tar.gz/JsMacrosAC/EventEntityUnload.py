from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .EntityHelper import EntityHelper

Entity = TypeVar["net.minecraft.entity.Entity"]
Entity_RemovalReason = TypeVar["net.minecraft.entity.Entity.RemovalReason"]

class EventEntityUnload(BaseEvent):
	entity: EntityHelper
	reason: str

	@overload
	def __init__(self, e: Entity, reason: Entity_RemovalReason) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


