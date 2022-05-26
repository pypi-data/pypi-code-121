from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .ItemStackHelper import ItemStackHelper

ItemStack = TypeVar["net.minecraft.item.ItemStack"]

class EventArmorChange(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	slot: str
	item: ItemStackHelper
	oldItem: ItemStackHelper

	@overload
	def __init__(self, slot: str, item: ItemStack, old: ItemStack) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


