from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper

StatusEffectInstance = TypeVar["net.minecraft.entity.effect.StatusEffectInstance"]

class StatusEffectHelper(BaseHelper):
	"""
	Since: 1.2.4 
	"""

	@overload
	def __init__(self, s: StatusEffectInstance) -> None:
		pass

	@overload
	def getId(self) -> str:
		"""
		Since: 1.2.4 
		"""
		pass

	@overload
	def getStrength(self) -> int:
		"""
		Since: 1.2.4 
		"""
		pass

	@overload
	def getTime(self) -> int:
		"""
		Since: 1.2.4 
		"""
		pass

	pass


