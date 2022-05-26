from typing import overload
from typing import List
from .BaseEvent import BaseEvent


class EventResourcePackLoaded(BaseEvent):
	"""This event is fired after resources have been reloaded, i.e. after the splash screen has finished.
This includes when the game is finished loading and the title screen becomes visible, which you can check using EventResourcePackLoaded#isGameStart .\n
	Since: 1.5.1 
	"""
	isGameStart: bool
	loadedPacks: List[str]

	@overload
	def __init__(self, isGameStart: bool) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


