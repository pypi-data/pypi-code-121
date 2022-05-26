from typing import overload
from .Inventory import Inventory


class LoomInventory(Inventory):
	"""
	Since: 1.5.1 
	"""

	@overload
	def selectPatternName(self, name: str) -> bool:
		"""
		Since: 1.5.1 

		Args:
			name: 

		Returns:
			success 
		"""
		pass

	@overload
	def selectPatternId(self, id: str) -> bool:
		"""
		Since: 1.5.1 

		Args:
			id: 

		Returns:
			success 
		"""
		pass

	@overload
	def selectPattern(self, index: int) -> bool:
		"""
		Since: 1.5.1 

		Args:
			index: 

		Returns:
			success 
		"""
		pass

	pass


