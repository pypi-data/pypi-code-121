from typing import overload
from .NBTElementHelper import NBTElementHelper


class NBTElementHelper_NBTNumberHelper(NBTElementHelper):
	"""
	Since: 1.5.1 
	"""

	@overload
	def asLong(self) -> float:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def asInt(self) -> int:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def asShort(self) -> float:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def asByte(self) -> float:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def asFloat(self) -> float:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def asDouble(self) -> float:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def asNumber(self) -> Number:
		"""
		Since: 1.5.1 
		"""
		pass

	pass


