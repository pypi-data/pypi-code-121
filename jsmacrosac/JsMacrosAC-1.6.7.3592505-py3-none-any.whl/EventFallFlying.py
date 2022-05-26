from typing import overload
from .BaseEvent import BaseEvent


class EventFallFlying(BaseEvent):
	state: bool

	@overload
	def __init__(self, state: bool) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


