from typing import overload
from .EventContainer import EventContainer
from .IEventListener import IEventListener


class EventLockWatchdog:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def startWatchdog(self, lock: EventContainer, listener: IEventListener, maxTime: float) -> None:
		pass

	pass


