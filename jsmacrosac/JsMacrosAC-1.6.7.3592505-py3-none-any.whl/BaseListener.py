from typing import overload
from .IEventListener import IEventListener
from .ScriptTrigger import ScriptTrigger
from .Core import Core
from .BaseEvent import BaseEvent
from .EventContainer import EventContainer


class BaseListener(IEventListener):
	"""This is for java-sided listeners, for creating listeners script sided directly use IEventListener
	"""

	@overload
	def __init__(self, trigger: ScriptTrigger, runner: Core) -> None:
		pass

	@overload
	def getRawTrigger(self) -> ScriptTrigger:
		pass

	@overload
	def runScript(self, event: BaseEvent) -> EventContainer:
		pass

	@overload
	def equals(self, o: object) -> bool:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


