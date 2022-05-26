from typing import overload
from typing import List
from .Inventory import Inventory
from .TextHelper import TextHelper


class EnchantInventory(Inventory):
	"""
	Since: 1.3.1 
	"""

	@overload
	def getRequiredLevels(self) -> List[int]:
		"""
		Since: 1.3.1 

		Returns:
			xp level required to do enchantments 
		"""
		pass

	@overload
	def getEnchantments(self) -> List[TextHelper]:
		"""
		Since: 1.3.1 

		Returns:
			list of enchantments text. 
		"""
		pass

	@overload
	def getEnchantmentIds(self) -> List[str]:
		"""
		Since: 1.3.1 

		Returns:
			id for enchantments 
		"""
		pass

	@overload
	def getEnchantmentLevels(self) -> List[int]:
		"""
		Since: 1.3.1 

		Returns:
			level of enchantments 
		"""
		pass

	@overload
	def doEnchant(self, index: int) -> bool:
		"""clicks the button to enchant.\n
		Since: 1.3.1 

		Args:
			index: 

		Returns:
			success 
		"""
		pass

	pass


