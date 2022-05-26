from typing import overload
from typing import List
from typing import Mapping
from typing import Set
from .Core import Core
from .ScriptTrigger import ScriptTrigger
from .IEventListener import IEventListener


class BaseEventRegistry:
	"""
	Since: 1.2.7 
	"""
	oldEvents: Mapping[str, str]
	events: Set[str]

	@overload
	def __init__(self, runner: Core) -> None:
		pass

	@overload
	def clearMacros(self) -> None:
		pass

	@overload
	def addScriptTrigger(self, rawmacro: ScriptTrigger) -> None:
		"""
		Since: 1.1.2 [citation needed] 

		Args:
			rawmacro: 
		"""
		pass

	@overload
	def addListener(self, event: str, listener: IEventListener) -> None:
		"""
		Since: 1.2.3 

		Args:
			listener: 
			event: 
		"""
		pass

	@overload
	def removeListener(self, event: str, listener: IEventListener) -> bool:
		"""
		Since: 1.2.3 

		Args:
			listener: 
			event: 
		"""
		pass

	@overload
	def removeListener(self, listener: IEventListener) -> bool:
		"""
		Since: 1.2.3 

		Args:
			listener: 
		"""
		pass

	@overload
	def removeScriptTrigger(self, rawmacro: ScriptTrigger) -> bool:
		"""
		Since: 1.1.2 [citation needed] 

		Args:
			rawmacro: 
		"""
		pass

	@overload
	def getListeners(self) -> Mapping[str, Set[IEventListener]]:
		"""
		Since: 1.2.3 
		"""
		pass

	@overload
	def getListeners(self, key: str) -> Set[IEventListener]:
		"""
		Since: 1.2.3 

		Args:
			key: 
		"""
		pass

	@overload
	def getScriptTriggers(self) -> List[ScriptTrigger]:
		"""
		Since: 1.1.2 [citation needed] 
		"""
		pass

	@overload
	def addEvent(self, eventName: str) -> None:
		"""
		Since: 1.1.2 [citation needed] 

		Args:
			eventName: 
		"""
		pass

	@overload
	def addEvent(self, clazz: Class) -> None:
		pass

	pass


