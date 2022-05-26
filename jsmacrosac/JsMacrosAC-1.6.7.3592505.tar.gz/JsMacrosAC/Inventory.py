from typing import overload
from typing import List
from typing import TypeVar
from typing import Mapping
from typing import Generic
from .ItemStackHelper import ItemStackHelper
from .RecipeHelper import RecipeHelper

T = TypeVar("T")
Screen = TypeVar["net.minecraft.client.gui.screen.Screen"]

class Inventory(Generic[T]):
	"""
	Since: 1.0.8 
	"""

	@overload
	def create(self) -> "Inventory":
		pass

	@overload
	def create(self, s: Screen) -> "Inventory":
		pass

	@overload
	def click(self, slot: int) -> "Inventory":
		"""
		Since: 1.5.0 

		Args:
			slot: 
		"""
		pass

	@overload
	def click(self, slot: int, mousebutton: int) -> "Inventory":
		"""Clicks a slot with a mouse button.\n
		Since: 1.0.8 

		Args:
			mousebutton: 
			slot: 
		"""
		pass

	@overload
	def dragClick(self, slots: List[int], mousebutton: int) -> "Inventory":
		"""Does a drag-click with a mouse button. (the slots don't have to be in order or even adjacent, but when vanilla minecraft calls the underlying function they're always sorted...)

		Args:
			slots: 
			mousebutton: 
		"""
		pass

	@overload
	def dropSlot(self, slot: int) -> "Inventory":
		"""
		Since: 1.5.0 

		Args:
			slot: 
		"""
		pass

	@overload
	def getSelectedHotbarSlotIndex(self) -> int:
		"""
		Since: 1.2.5 

		Returns:
			the index of the selected hotbar slot. 
		"""
		pass

	@overload
	def setSelectedHotbarSlotIndex(self, index: int) -> None:
		"""
		Since: 1.2.5 

		Args:
			index: 
		"""
		pass

	@overload
	def closeAndDrop(self) -> "Inventory":
		"""closes the inventory, (if the inventory/container is visible it will close the gui). also drops any "held on mouse" items.
		"""
		pass

	@overload
	def close(self) -> None:
		"""Closes the inventory, and open gui if applicable.
		"""
		pass

	@overload
	def quick(self, slot: int) -> "Inventory":
		"""simulates a shift-click on a slot.
It should be safe to chain these without FClient#waitTick() at least for a bunch of the same item.

		Args:
			slot: 
		"""
		pass

	@overload
	def getHeld(self) -> ItemStackHelper:
		"""

		Returns:
			the held (by the mouse) item. 
		"""
		pass

	@overload
	def getSlot(self, slot: int) -> ItemStackHelper:
		"""

		Args:
			slot: 

		Returns:
			the item in the slot. 
		"""
		pass

	@overload
	def getTotalSlots(self) -> int:
		"""

		Returns:
			the size of the container/inventory. 
		"""
		pass

	@overload
	def split(self, slot1: int, slot2: int) -> "Inventory":
		"""Splits the held stack into two slots. can be alternatively done with Inventory#dragClick(int[],int) if this one has issues on some servers.

		Args:
			slot2: 
			slot1: 
		"""
		pass

	@overload
	def grabAll(self, slot: int) -> "Inventory":
		"""Does that double click thingy to turn a incomplete stack pickup into a complete stack pickup if you have more in your inventory.

		Args:
			slot: 
		"""
		pass

	@overload
	def swap(self, slot1: int, slot2: int) -> "Inventory":
		"""swaps the items in two slots.

		Args:
			slot2: 
			slot1: 
		"""
		pass

	@overload
	def swapHotbar(self, slot: int, hotbarSlot: int) -> "Inventory":
		"""equivelent to hitting the numbers or f for swapping slots to hotbar

		Args:
			hotbarSlot: 0-8 or 40 for offhand 
			slot: 
		"""
		pass

	@overload
	def openGui(self) -> None:
		"""
		Since: 1.2.8 
		"""
		pass

	@overload
	def getSlotUnderMouse(self) -> int:
		"""
		Since: 1.1.3 

		Returns:
			the id of the slot under the mouse. 
		"""
		pass

	@overload
	def getType(self) -> str:
		"""
		Since: 1.1.3 

		Returns:
			the part of the mapping the slot is in. 
		"""
		pass

	@overload
	def getMap(self) -> Mapping[str, List[int]]:
		"""
		Since: 1.1.3 

		Returns:
			the inventory mappings different depending on the type of open container/inventory. 
		"""
		pass

	@overload
	def getLocation(self, slotNum: int) -> str:
		"""
		Since: 1.1.3 

		Args:
			slotNum: 

		Returns:
			returns the part of the mapping the slot is in. 
		"""
		pass

	@overload
	def getCraftableRecipes(self) -> List[RecipeHelper]:
		"""
		Since: 1.3.1 

		Returns:
			all craftable recipes 
		"""
		pass

	@overload
	def getContainerTitle(self) -> str:
		"""
		Since: 1.2.3 
		"""
		pass

	@overload
	def getRawContainer(self) -> T:
		pass

	@overload
	def toString(self) -> str:
		pass

	@overload
	def getCurrentSyncId(self) -> int:
		"""
		Since: 1.6.0 
		"""
		pass

	pass


