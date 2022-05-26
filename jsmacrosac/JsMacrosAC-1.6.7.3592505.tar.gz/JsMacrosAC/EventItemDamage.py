from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .ItemStackHelper import ItemStackHelper

ItemStack = TypeVar["net.minecraft.item.ItemStack"]

class EventItemDamage(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	item: ItemStackHelper
	damage: int

	@overload
	def __init__(self, stack: ItemStack, damage: int) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


