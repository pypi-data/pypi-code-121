from typing import overload
from .BaseEvent import BaseEvent


class EventAirChange(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	air: int

	@overload
	def __init__(self, air: int) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


