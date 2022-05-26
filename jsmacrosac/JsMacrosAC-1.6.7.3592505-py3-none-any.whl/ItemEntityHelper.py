from typing import overload
from typing import TypeVar
from .EntityHelper import EntityHelper
from .ItemStackHelper import ItemStackHelper

ItemEntity = TypeVar["net.minecraft.entity.ItemEntity"]

class ItemEntityHelper(EntityHelper):

	@overload
	def __init__(self, e: ItemEntity) -> None:
		pass

	@overload
	def getContainedItemStack(self) -> ItemStackHelper:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


