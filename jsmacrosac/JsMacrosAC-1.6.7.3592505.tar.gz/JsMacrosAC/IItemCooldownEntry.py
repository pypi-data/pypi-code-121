from typing import overload


class IItemCooldownEntry:

	@overload
	def getStartTick(self) -> int:
		pass

	@overload
	def getEndTick(self) -> int:
		pass

	pass


