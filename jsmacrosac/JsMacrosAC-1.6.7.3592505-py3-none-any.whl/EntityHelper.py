from typing import overload
from typing import List
from typing import TypeVar
from typing import Generic
from .BaseHelper import BaseHelper
from .PositionCommon_Pos3D import PositionCommon_Pos3D
from .PositionCommon_Pos2D import PositionCommon_Pos2D
from .TextHelper import TextHelper
from .NBTElementHelper import NBTElementHelper
from .ClientPlayerEntityHelper import ClientPlayerEntityHelper
from .PlayerEntityHelper import PlayerEntityHelper
from .VillagerEntityHelper import VillagerEntityHelper
from .MerchantEntityHelper import MerchantEntityHelper
from .LivingEntityHelper import LivingEntityHelper
from .ItemEntityHelper import ItemEntityHelper

Entity = TypeVar["net.minecraft.entity.Entity"]
T = TypeVar("T")

class EntityHelper(Generic[T], BaseHelper):
	"""
	"""

	@overload
	def getPos(self) -> PositionCommon_Pos3D:
		"""

		Returns:
			entity position. 
		"""
		pass

	@overload
	def getBlockPos(self) -> PositionCommon_Pos3D:
		"""
		Since: 1.6.5 

		Returns:
			entity block position. 
		"""
		pass

	@overload
	def getChunkPos(self) -> PositionCommon_Pos2D:
		"""
		Since: 1.6.5 

		Returns:
			entity chunk coordinates. Since Pos2D only has x and y fields, z coord is y. 
		"""
		pass

	@overload
	def getX(self) -> float:
		"""
		Since: 1.0.8 

		Returns:
			the 'x' value of the entity. 
		"""
		pass

	@overload
	def getY(self) -> float:
		"""
		Since: 1.0.8 

		Returns:
			the 'y' value of the entity. 
		"""
		pass

	@overload
	def getZ(self) -> float:
		"""
		Since: 1.0.8 

		Returns:
			the 'z' value of the entity. 
		"""
		pass

	@overload
	def getEyeHeight(self) -> float:
		"""
		Since: 1.2.8 

		Returns:
			the current eye height offset for the entitye. 
		"""
		pass

	@overload
	def getPitch(self) -> float:
		"""
		Since: 1.0.8 

		Returns:
			the 'pitch' value of the entity. 
		"""
		pass

	@overload
	def getYaw(self) -> float:
		"""
		Since: 1.0.8 

		Returns:
			the 'yaw' value of the entity. 
		"""
		pass

	@overload
	def getName(self) -> TextHelper:
		"""
		Since: 1.0.8 [citation needed], returned string until 1.6.4 

		Returns:
			the name of the entity. 
		"""
		pass

	@overload
	def getType(self) -> str:
		"""

		Returns:
			the type of the entity. 
		"""
		pass

	@overload
	def isGlowing(self) -> bool:
		"""
		Since: 1.1.9 

		Returns:
			if the entity has the glowing effect. 
		"""
		pass

	@overload
	def isInLava(self) -> bool:
		"""
		Since: 1.1.9 

		Returns:
			if the entity is in lava. 
		"""
		pass

	@overload
	def isOnFire(self) -> bool:
		"""
		Since: 1.1.9 

		Returns:
			if the entity is on fire. 
		"""
		pass

	@overload
	def getVehicle(self) -> "EntityHelper":
		"""
		Since: 1.1.8 [citation needed] 

		Returns:
			the vehicle of the entity. 
		"""
		pass

	@overload
	def getPassengers(self) -> List["EntityHelper"]:
		"""
		Since: 1.1.8 [citation needed] 

		Returns:
			the entity passengers. 
		"""
		pass

	@overload
	def getNBT(self) -> NBTElementHelper:
		"""
		Since: 1.2.8, was a String until 1.5.0 
		"""
		pass

	@overload
	def setCustomName(self, name: TextHelper) -> None:
		"""
		Since: 1.6.4 

		Args:
			name: 
		"""
		pass

	@overload
	def setGlowingColor(self, color: int) -> None:
		"""

		Args:
			color: 
		"""
		pass

	@overload
	def resetGlowingColor(self) -> None:
		"""
		"""
		pass

	@overload
	def setGlowing(self, val: bool) -> "EntityHelper":
		"""Sets whether the entity is glowing.\n
		Since: 1.1.9 

		Args:
			val: 
		"""
		pass

	@overload
	def resetGlowing(self) -> "EntityHelper":
		"""reset the glowing effect to proper value.\n
		Since: 1.6.3 
		"""
		pass

	@overload
	def isAlive(self) -> bool:
		"""Checks if the entity is still alive.\n
		Since: 1.2.8 
		"""
		pass

	@overload
	def getUUID(self) -> str:
		"""
		Since: 1.6.5 

		Returns:
			UUID of the entity, random* if not a player, otherwise the player's uuid. 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	@overload
	def create(self, e: Entity) -> "EntityHelper":
		"""mostly for internal use.

		Args:
			e: mc entity. 

		Returns:
			correct subclass of this. 
		"""
		pass

	@overload
	def asClientPlayer(self) -> ClientPlayerEntityHelper:
		"""
		Since: 1.6.3 

		Returns:
			cast of this entity helper (mainly for typescript) 
		"""
		pass

	@overload
	def asPlayer(self) -> PlayerEntityHelper:
		"""
		Since: 1.6.3 

		Returns:
			cast of this entity helper (mainly for typescript) 
		"""
		pass

	@overload
	def asVillager(self) -> VillagerEntityHelper:
		"""
		Since: 1.6.3 

		Returns:
			cast of this entity helper (mainly for typescript) 
		"""
		pass

	@overload
	def asMerchant(self) -> MerchantEntityHelper:
		"""
		Since: 1.6.3 

		Returns:
			cast of this entity helper (mainly for typescript) 
		"""
		pass

	@overload
	def asLiving(self) -> LivingEntityHelper:
		"""
		Since: 1.6.3 

		Returns:
			cast of this entity helper (mainly for typescript) 
		"""
		pass

	@overload
	def asItem(self) -> ItemEntityHelper:
		"""
		Since: 1.6.3 

		Returns:
			cast of this entity helper (mainly for typescript) 
		"""
		pass

	pass


