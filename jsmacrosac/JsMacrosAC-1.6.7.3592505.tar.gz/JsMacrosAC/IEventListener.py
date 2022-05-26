from typing import overload
from .BaseEvent import BaseEvent
from .EventContainer import EventContainer


class IEventListener:

	@overload
	def trigger(self, event: BaseEvent) -> EventContainer:
		pass

	pass


