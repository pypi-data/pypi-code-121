from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .Inventory import Inventory
from .IScreen import IScreen

HandledScreen = TypeVar["net.minecraft.client.gui.screen.ingame.HandledScreen__"]

class EventOpenContainer(BaseEvent):
	"""
	Since: 1.6.5 
	"""
	inventory: Inventory
	screen: IScreen
	cancelled: bool

	@overload
	def __init__(self, screen: HandledScreen) -> None:
		pass

	pass


