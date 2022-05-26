from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .IScreen import IScreen

Screen = TypeVar["net.minecraft.client.gui.screen.Screen"]

class EventOpenScreen(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	screen: IScreen
	screenName: str

	@overload
	def __init__(self, screen: Screen) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


