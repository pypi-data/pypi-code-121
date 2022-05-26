from typing import overload
from .IChunkSection import IChunkSection


class MixinChunkSelection(IChunkSection):

	@overload
	def __init__(self) -> None:
		pass

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


