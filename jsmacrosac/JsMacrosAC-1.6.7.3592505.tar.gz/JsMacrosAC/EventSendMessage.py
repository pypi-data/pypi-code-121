from typing import overload
from .BaseEvent import BaseEvent


class EventSendMessage(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	message: str

	@overload
	def __init__(self, message: str) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


