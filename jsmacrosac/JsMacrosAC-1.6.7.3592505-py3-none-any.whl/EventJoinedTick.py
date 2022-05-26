from typing import overload
from .BaseEvent import BaseEvent


class EventJoinedTick(BaseEvent):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


