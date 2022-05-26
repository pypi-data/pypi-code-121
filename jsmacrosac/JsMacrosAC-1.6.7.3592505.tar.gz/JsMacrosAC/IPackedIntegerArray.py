from typing import overload


class IPackedIntegerArray:

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


