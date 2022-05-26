from typing import overload


class IChunkSection:

	@overload
	def jsmacros_getNonEmptyBlockCount(self) -> float:
		pass

	@overload
	def jsmacros_getRandomTickableBlockCount(self) -> float:
		pass

	@overload
	def jsmacros_getNonEmptyFluidCount(self) -> float:
		pass

	pass


