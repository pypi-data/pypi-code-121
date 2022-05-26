from typing import overload
from .BaseEvent import BaseEvent


class EventDimensionChange(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	dimension: str

	@overload
	def __init__(self, dimension: str) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


