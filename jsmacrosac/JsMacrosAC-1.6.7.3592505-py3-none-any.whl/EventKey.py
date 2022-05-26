from typing import overload
from .BaseEvent import BaseEvent


class EventKey(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	action: int
	key: str
	mods: str

	@overload
	def __init__(self, key: int, scancode: int, action: int, mods: int) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	@overload
	def getKeyModifiers(self, mods: int) -> str:
		"""turn an Integer for key modifiers into a Translation Key.

		Args:
			mods: 
		"""
		pass

	@overload
	def getModInt(self, mods: str) -> int:
		"""turn a Translation Key for modifiers into an Integer .

		Args:
			mods: 
		"""
		pass

	pass


