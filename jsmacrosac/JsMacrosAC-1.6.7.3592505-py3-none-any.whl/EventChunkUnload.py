from typing import overload
from .BaseEvent import BaseEvent


class EventChunkUnload(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	x: int
	z: int

	@overload
	def __init__(self, x: int, z: int) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


