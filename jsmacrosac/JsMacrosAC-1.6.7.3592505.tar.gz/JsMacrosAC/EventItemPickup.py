from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .ItemStackHelper import ItemStackHelper

ItemStack = TypeVar["net.minecraft.item.ItemStack"]

class EventItemPickup(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	item: ItemStackHelper

	@overload
	def __init__(self, item: ItemStack) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


