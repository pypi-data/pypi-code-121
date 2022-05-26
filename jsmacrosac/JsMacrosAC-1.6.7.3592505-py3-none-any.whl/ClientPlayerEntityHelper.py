from typing import overload
from typing import TypeVar
from typing import Mapping
from typing import Generic
from .PlayerEntityHelper import PlayerEntityHelper
from .EntityHelper import EntityHelper

T = TypeVar("T")

class ClientPlayerEntityHelper(Generic[T], PlayerEntityHelper):
	"""
	Since: 1.0.3 
	"""

	@overload
	def __init__(self, e: T) -> None:
		pass

	@overload
	def lookAt(self, yaw: float, pitch: float) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.0.3 

		Args:
			pitch: (was yaw prior to 1.2.6) 
			yaw: (was pitch prior to 1.2.6) 
		"""
		pass

	@overload
	def lookAt(self, x: float, y: float, z: float) -> "ClientPlayerEntityHelper":
		"""look at the specified coordinates.\n
		Since: 1.2.8 

		Args:
			x: 
			y: 
			z: 
		"""
		pass

	@overload
	def attack(self, entity: EntityHelper) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.5.0 

		Args:
			entity: 
		"""
		pass

	@overload
	def attack(self, entity: EntityHelper, await_: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.6.0 

		Args:
			await: 
			entity: 
		"""
		pass

	@overload
	def attack(self, x: int, y: int, z: int, direction: int) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.5.0 

		Args:
			x: 
			y: 
			z: 
			direction: 0-5 in order: [DOWN, UP, NORTH, SOUTH, WEST, EAST]; 
		"""
		pass

	@overload
	def attack(self, x: int, y: int, z: int, direction: int, await_: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.6.0 

		Args:
			x: 
			await: 
			y: 
			z: 
			direction: 0-5 in order: [DOWN, UP, NORTH, SOUTH, WEST, EAST]; 
		"""
		pass

	@overload
	def interactEntity(self, entity: EntityHelper, offHand: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.5.0, renamed from 'interact' in 1.6.0 

		Args:
			entity: 
			offHand: 
		"""
		pass

	@overload
	def interactEntity(self, entity: EntityHelper, offHand: bool, await_: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.6.0 

		Args:
			await: 
			entity: 
			offHand: 
		"""
		pass

	@overload
	def interactItem(self, offHand: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.5.0, renamed from 'interact' in 1.6.0 

		Args:
			offHand: 
		"""
		pass

	@overload
	def interactItem(self, offHand: bool, await_: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.6.0 

		Args:
			await: 
			offHand: 
		"""
		pass

	@overload
	def interactBlock(self, x: int, y: int, z: int, direction: int, offHand: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.5.0, renamed from 'interact' in 1.6.0 

		Args:
			x: 
			y: 
			z: 
			direction: 
			offHand: 
		"""
		pass

	@overload
	def interactBlock(self, x: int, y: int, z: int, direction: int, offHand: bool, await_: bool) -> "ClientPlayerEntityHelper":
		pass

	@overload
	def interact(self) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.5.0 
		"""
		pass

	@overload
	def interact(self, await_: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.6.0 

		Args:
			await: 
		"""
		pass

	@overload
	def attack(self) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.5.0 
		"""
		pass

	@overload
	def attack(self, await_: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.6.0 

		Args:
			await: 
		"""
		pass

	@overload
	def setLongAttack(self, stop: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.6.3 

		Args:
			stop: 
		"""
		pass

	@overload
	def setLongInteract(self, stop: bool) -> "ClientPlayerEntityHelper":
		"""
		Since: 1.6.3 

		Args:
			stop: 
		"""
		pass

	@overload
	def getItemCooldownsRemainingTicks(self) -> Mapping[str, int]:
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def getItemCooldownRemainingTicks(self, item: str) -> int:
		"""
		Since: 1.6.5 

		Args:
			item: 
		"""
		pass

	@overload
	def getTicksSinceCooldownsStart(self) -> Mapping[str, int]:
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def getTicksSinceCooldownStart(self, item: str) -> int:
		"""
		Since: 1.6.5 

		Args:
			item: 
		"""
		pass

	@overload
	def getFoodLevel(self) -> int:
		"""
		Since: 1.1.2 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


