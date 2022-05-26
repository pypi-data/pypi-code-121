from typing import overload
from .NBTElementHelper import NBTElementHelper


class NBTElementHelper_NBTListHelper(NBTElementHelper):
	"""
	Since: 1.5.1 
	"""

	@overload
	def length(self) -> int:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def get(self, index: int) -> NBTElementHelper:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def getHeldType(self) -> int:
		"""
		Since: 1.5.1 
		"""
		pass

	pass


