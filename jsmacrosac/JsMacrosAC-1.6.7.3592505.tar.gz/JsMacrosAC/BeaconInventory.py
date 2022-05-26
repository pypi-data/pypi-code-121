from typing import overload
from .Inventory import Inventory


class BeaconInventory(Inventory):
	"""
	Since: 1.5.1 
	"""

	@overload
	def getLevel(self) -> int:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def getFirstEffect(self) -> str:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def getSecondEffect(self) -> str:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def selectFirstEffect(self, id: str) -> bool:
		"""
		Since: 1.5.1 

		Args:
			id: 
		"""
		pass

	@overload
	def selectSecondEffect(self, id: str) -> bool:
		"""
		Since: 1.5.1 

		Args:
			id: 
		"""
		pass

	@overload
	def applyEffects(self) -> bool:
		"""
		Since: 1.5.1 
		"""
		pass

	pass


