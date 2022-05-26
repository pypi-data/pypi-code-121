from typing import overload
from typing import TypeVar
from typing import Mapping
from .IItemCooldownEntry import IItemCooldownEntry

Item = TypeVar["net.minecraft.item.Item"]

class IItemCooldownManager:

	@overload
	def getCooldownItems(self) -> Mapping[Item, IItemCooldownEntry]:
		pass

	@overload
	def getManagerTicks(self) -> int:
		pass

	pass


