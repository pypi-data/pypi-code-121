from typing import overload
from typing import List
from typing import TypeVar
from typing import Generic
from .EntityHelper import EntityHelper
from .StatusEffectHelper import StatusEffectHelper
from .ItemStackHelper import ItemStackHelper

T = TypeVar("T")

class LivingEntityHelper(Generic[T], EntityHelper):

	@overload
	def __init__(self, e: T) -> None:
		pass

	@overload
	def getStatusEffects(self) -> List[StatusEffectHelper]:
		"""
		Since: 1.2.7 

		Returns:
			entity status effects. 
		"""
		pass

	@overload
	def getMainHand(self) -> ItemStackHelper:
		"""
		Since: 1.2.7 

		Returns:
			the item in the entity's main hand. 
		"""
		pass

	@overload
	def getOffHand(self) -> ItemStackHelper:
		"""
		Since: 1.2.7 

		Returns:
			the item in the entity's off hand. 
		"""
		pass

	@overload
	def getHeadArmor(self) -> ItemStackHelper:
		"""
		Since: 1.2.7 

		Returns:
			the item in the entity's head armor slot. 
		"""
		pass

	@overload
	def getChestArmor(self) -> ItemStackHelper:
		"""
		Since: 1.2.7 

		Returns:
			the item in the entity's chest armor slot. 
		"""
		pass

	@overload
	def getLegArmor(self) -> ItemStackHelper:
		"""
		Since: 1.2.7 

		Returns:
			the item in the entity's leg armor slot. 
		"""
		pass

	@overload
	def getFootArmor(self) -> ItemStackHelper:
		"""
		Since: 1.2.7 

		Returns:
			the item in the entity's foot armor slot. 
		"""
		pass

	@overload
	def getHealth(self) -> float:
		"""
		Since: 1.3.1 

		Returns:
			entity's health 
		"""
		pass

	@overload
	def getMaxHealth(self) -> float:
		"""
		Since: 1.6.5 

		Returns:
			entity's max health 
		"""
		pass

	@overload
	def isSleeping(self) -> bool:
		"""
		Since: 1.2.7 

		Returns:
			if the entity is in a bed. 
		"""
		pass

	@overload
	def isFallFlying(self) -> bool:
		"""
		Since: 1.5.0 

		Returns:
			if the entity has elytra deployed 
		"""
		pass

	pass


