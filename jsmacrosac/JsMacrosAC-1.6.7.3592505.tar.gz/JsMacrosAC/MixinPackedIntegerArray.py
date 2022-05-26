from typing import overload
from .IPackedIntegerArray import IPackedIntegerArray


class MixinPackedIntegerArray(IPackedIntegerArray):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_getMaxValue(self) -> float:
		pass

	@overload
	def jsmacros_getElementsPerLong(self) -> int:
		pass

	@overload
	def jsmacros_getIndexScale(self) -> int:
		pass

	@overload
	def jsmacros_getIndexOffset(self) -> int:
		pass

	@overload
	def jsmacros_getIndexShift(self) -> int:
		pass

	pass


