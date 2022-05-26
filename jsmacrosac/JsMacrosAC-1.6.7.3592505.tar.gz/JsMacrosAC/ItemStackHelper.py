from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper
from .TextHelper import TextHelper
from .NBTElementHelper import NBTElementHelper

ItemStack = TypeVar["net.minecraft.item.ItemStack"]

class ItemStackHelper(BaseHelper):
	"""
	"""

	@overload
	def __init__(self, i: ItemStack) -> None:
		pass

	@overload
	def setDamage(self, damage: int) -> "ItemStackHelper":
		"""Sets the item damage value.

You may want to use ItemStackHelper#copy() first.\n
		Since: 1.2.0 

		Args:
			damage: 
		"""
		pass

	@overload
	def isDamageable(self) -> bool:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def isEnchantable(self) -> bool:
		"""
		Since: 1.2.0 
		"""
		pass

	@overload
	def getDamage(self) -> int:
		"""
		"""
		pass

	@overload
	def getMaxDamage(self) -> int:
		"""
		"""
		pass

	@overload
	def getDefaultName(self) -> TextHelper:
		"""
		Since: 1.2.0 

		Returns:
			was string before 1.6.5 
		"""
		pass

	@overload
	def getName(self) -> TextHelper:
		"""

		Returns:
			was string before 1.6.5 
		"""
		pass

	@overload
	def getCount(self) -> int:
		"""
		"""
		pass

	@overload
	def getMaxCount(self) -> int:
		"""
		"""
		pass

	@overload
	def getNBT(self) -> NBTElementHelper:
		"""
		Since: 1.1.6, was a String until 1.5.1 
		"""
		pass

	@overload
	def getCreativeTab(self) -> str:
		"""
		Since: 1.1.3 
		"""
		pass

	@overload
	def getItemID(self) -> str:
		"""
		"""
		pass

	@overload
	def getItemId(self) -> str:
		"""
		Since: 1.6.4 
		"""
		pass

	@overload
	def isEmpty(self) -> bool:
		"""
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	@overload
	def equals(self, ish: "ItemStackHelper") -> bool:
		"""
		Since: 1.1.3 [citation needed] 

		Args:
			ish: 
		"""
		pass

	@overload
	def equals(self, is_: ItemStack) -> bool:
		"""
		Since: 1.1.3 [citation needed] 

		Args:
			is: 
		"""
		pass

	@overload
	def isItemEqual(self, ish: "ItemStackHelper") -> bool:
		"""
		Since: 1.1.3 [citation needed] 

		Args:
			ish: 
		"""
		pass

	@overload
	def isItemEqual(self, is_: ItemStack) -> bool:
		"""
		Since: 1.1.3 [citation needed] 

		Args:
			is: 
		"""
		pass

	@overload
	def isItemEqualIgnoreDamage(self, ish: "ItemStackHelper") -> bool:
		"""
		Since: 1.1.3 [citation needed] 

		Args:
			ish: 
		"""
		pass

	@overload
	def isItemEqualIgnoreDamage(self, is_: ItemStack) -> bool:
		"""
		Since: 1.1.3 [citation needed] 

		Args:
			is: 
		"""
		pass

	@overload
	def isNBTEqual(self, ish: "ItemStackHelper") -> bool:
		"""
		Since: 1.1.3 [citation needed] 

		Args:
			ish: 
		"""
		pass

	@overload
	def isNBTEqual(self, is_: ItemStack) -> bool:
		"""
		Since: 1.1.3 [citation needed] 

		Args:
			is: 
		"""
		pass

	@overload
	def isOnCooldown(self) -> bool:
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def getCooldownProgress(self) -> float:
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def copy(self) -> "ItemStackHelper":
		"""
		Since: 1.2.0 
		"""
		pass

	pass


