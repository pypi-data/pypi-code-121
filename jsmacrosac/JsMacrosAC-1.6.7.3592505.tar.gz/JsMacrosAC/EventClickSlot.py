from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .Inventory import Inventory

HandledScreen = TypeVar["net.minecraft.client.gui.screen.ingame.HandledScreen__"]

class EventClickSlot(BaseEvent):
	"""event triggered when the user "clicks" a slot in an inventory\n
	Since: 1.6.4 
	"""
	mode: int
	button: int
	slot: int
	cancel: bool

	@overload
	def __init__(self, screen: HandledScreen, mode: int, button: int, slot: int) -> None:
		pass

	@overload
	def getInventory(self) -> Inventory:
		"""

		Returns:
			inventory associated with the event 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


