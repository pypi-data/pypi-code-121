from typing import overload
from .BaseListener import BaseListener
from .ScriptTrigger import ScriptTrigger
from .Core import Core
from .BaseEvent import BaseEvent
from .EventContainer import EventContainer


class KeyListener(BaseListener):

	@overload
	def __init__(self, macro: ScriptTrigger, runner: Core) -> None:
		pass

	@overload
	def trigger(self, event: BaseEvent) -> EventContainer:
		pass

	pass


