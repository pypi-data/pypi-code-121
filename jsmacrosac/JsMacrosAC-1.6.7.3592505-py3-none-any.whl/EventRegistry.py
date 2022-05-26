from typing import overload
from typing import List
from .BaseEventRegistry import BaseEventRegistry
from .Core import Core
from .ScriptTrigger import ScriptTrigger


class EventRegistry(BaseEventRegistry):

	@overload
	def __init__(self, runner: Core) -> None:
		pass

	@overload
	def addScriptTrigger(self, rawmacro: ScriptTrigger) -> None:
		pass

	@overload
	def removeScriptTrigger(self, rawmacro: ScriptTrigger) -> bool:
		pass

	@overload
	def getScriptTriggers(self) -> List[ScriptTrigger]:
		pass

	pass


