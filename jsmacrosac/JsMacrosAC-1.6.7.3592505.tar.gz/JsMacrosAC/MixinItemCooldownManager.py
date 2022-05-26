from typing import overload
from typing import TypeVar
from typing import Mapping
from .IItemCooldownManager import IItemCooldownManager
from .IItemCooldownEntry import IItemCooldownEntry

Item = TypeVar["net.minecraft.item.Item"]

class MixinItemCooldownManager(IItemCooldownManager):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def getCooldownItems(self) -> Mapping[Item, IItemCooldownEntry]:
		pass

	@overload
	def getManagerTicks(self) -> int:
		pass

	pass


