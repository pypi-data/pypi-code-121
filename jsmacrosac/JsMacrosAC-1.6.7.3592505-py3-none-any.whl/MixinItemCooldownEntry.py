from typing import overload
from .IItemCooldownEntry import IItemCooldownEntry


class MixinItemCooldownEntry(IItemCooldownEntry):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def getStartTick(self) -> int:
		pass

	@overload
	def getEndTick(self) -> int:
		pass

	pass


