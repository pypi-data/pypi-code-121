from typing import overload
from .BaseEvent import BaseEvent


class EventHungerChange(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	foodLevel: int

	@overload
	def __init__(self, foodLevel: int) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


