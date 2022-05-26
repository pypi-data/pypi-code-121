from typing import overload
from .BaseEvent import BaseEvent


class EventTick(BaseEvent):
	"""
	Since: 1.2.7 
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


