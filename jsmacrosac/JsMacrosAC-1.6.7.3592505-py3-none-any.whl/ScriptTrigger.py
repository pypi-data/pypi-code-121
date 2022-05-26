from typing import overload
from typing import TypeVar
from .ScriptTrigger_TriggerType import ScriptTrigger_TriggerType

File = TypeVar["java.io.File"]

class ScriptTrigger:
	triggerType: ScriptTrigger_TriggerType
	event: str
	scriptFile: str
	enabled: bool

	@overload
	def __init__(self, triggerType: ScriptTrigger_TriggerType, event: str, scriptFile: File, enabled: bool) -> None:
		pass

	@overload
	def __init__(self, triggerType: ScriptTrigger_TriggerType, event: str, scriptFile: str, enabled: bool) -> None:
		pass

	@overload
	def equals(self, macro: "ScriptTrigger") -> bool:
		pass

	@overload
	def toString(self) -> str:
		pass

	@overload
	def copy(self, m: "ScriptTrigger") -> "ScriptTrigger":
		pass

	@overload
	def copy(self) -> "ScriptTrigger":
		pass

	@overload
	def getTriggerType(self) -> ScriptTrigger_TriggerType:
		"""
		Since: 1.2.7 
		"""
		pass

	@overload
	def getEvent(self) -> str:
		"""
		Since: 1.2.7 
		"""
		pass

	@overload
	def getScriptFile(self) -> str:
		"""
		Since: 1.2.7 
		"""
		pass

	@overload
	def getEnabled(self) -> bool:
		"""
		Since: 1.2.7 
		"""
		pass

	pass


