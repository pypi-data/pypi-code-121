from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper

PlayerAbilities = TypeVar["net.minecraft.entity.player.PlayerAbilities"]

class PlayerAbilitiesHelper(BaseHelper):
	"""
	Since: 1.0.3 
	"""

	@overload
	def __init__(self, a: PlayerAbilities) -> None:
		pass

	@overload
	def getInvulnerable(self) -> bool:
		"""
		Since: 1.0.3 

		Returns:
			whether the player can be damaged. 
		"""
		pass

	@overload
	def getFlying(self) -> bool:
		"""
		Since: 1.0.3 

		Returns:
			if the player is currently flying. 
		"""
		pass

	@overload
	def getAllowFlying(self) -> bool:
		"""
		Since: 1.0.3 

		Returns:
			if the player is allowed to fly. 
		"""
		pass

	@overload
	def getCreativeMode(self) -> bool:
		"""
		Since: 1.0.3 

		Returns:
			if the player is in creative. 
		"""
		pass

	@overload
	def setFlying(self, b: bool) -> "PlayerAbilitiesHelper":
		"""set the player flying state.\n
		Since: 1.0.3 

		Args:
			b: 
		"""
		pass

	@overload
	def setAllowFlying(self, b: bool) -> "PlayerAbilitiesHelper":
		"""set the player allow flying state.\n
		Since: 1.0.3 

		Args:
			b: 
		"""
		pass

	@overload
	def getFlySpeed(self) -> float:
		"""
		Since: 1.0.3 

		Returns:
			the player fly speed multiplier. 
		"""
		pass

	@overload
	def setFlySpeed(self, flySpeed: float) -> "PlayerAbilitiesHelper":
		"""set the player fly speed multiplier.\n
		Since: 1.0.3 

		Args:
			flySpeed: 
		"""
		pass

	pass


