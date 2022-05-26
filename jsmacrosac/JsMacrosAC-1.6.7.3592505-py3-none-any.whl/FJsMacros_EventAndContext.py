from typing import overload
from .BaseEvent import BaseEvent
from .EventContainer import EventContainer


class FJsMacros_EventAndContext:
	event: BaseEvent
	context: EventContainer

	@overload
	def __init__(self, event: BaseEvent, context: EventContainer) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


