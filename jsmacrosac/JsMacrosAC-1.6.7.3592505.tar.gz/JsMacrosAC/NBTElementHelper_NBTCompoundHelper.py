from typing import overload
from typing import Set
from .NBTElementHelper import NBTElementHelper


class NBTElementHelper_NBTCompoundHelper(NBTElementHelper):
	"""
	Since: 1.5.1 
	"""

	@overload
	def getKeys(self) -> Set[str]:
		"""
		Since: 1.6.0 
		"""
		pass

	@overload
	def getType(self, key: str) -> int:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def has(self, key: str) -> bool:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def get(self, key: str) -> NBTElementHelper:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def asString(self, key: str) -> str:
		"""
		Since: 1.5.1 
		"""
		pass

	pass


