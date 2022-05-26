from typing import overload
from typing import TypeVar
from .MerchantEntityHelper import MerchantEntityHelper

VillagerEntity = TypeVar["net.minecraft.entity.passive.VillagerEntity"]

class VillagerEntityHelper(MerchantEntityHelper):
	"""
	Since: 1.6.3 
	"""

	@overload
	def __init__(self, e: VillagerEntity) -> None:
		pass

	@overload
	def getProfession(self) -> str:
		"""
		Since: 1.6.3 
		"""
		pass

	@overload
	def getStyle(self) -> str:
		"""
		Since: 1.6.3 
		"""
		pass

	@overload
	def getLevel(self) -> int:
		"""
		Since: 1.6.3 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


