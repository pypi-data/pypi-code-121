from typing import overload
from typing import List
from typing import TypeVar
from .MethodWrapper import MethodWrapper

Function = TypeVar["java.util.function.Function_java.lang.String,xyz.wagyourtail.jsmacros.client.api.classes.CommandBuilder_"]

class CommandBuilder:
	"""
	Since: 1.4.2 
	"""
	createNewBuilder: Function

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def literalArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def angleArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def blockArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def booleanArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def colorArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def doubleArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def doubleArg(self, name: str, min: float, max: float) -> "CommandBuilder":
		pass

	@overload
	def floatRangeArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def longArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def longArg(self, name: str, min: float, max: float) -> "CommandBuilder":
		pass

	@overload
	def identifierArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def intArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def intArg(self, name: str, min: int, max: int) -> "CommandBuilder":
		pass

	@overload
	def intRangeArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def itemArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def nbtArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def greedyStringArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def quotedStringArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def wordArg(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def textArgType(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def uuidArgType(self, name: str) -> "CommandBuilder":
		pass

	@overload
	def regexArgType(self, name: str, regex: str, flags: str) -> "CommandBuilder":
		pass

	@overload
	def executes(self, callback: MethodWrapper) -> "CommandBuilder":
		"""it is recomended to use FJsMacros#runScript(java.lang.String,xyz.wagyourtail.jsmacros.core.event.BaseEvent) in the callback if you expect to actually do anything complicated with waits.

the CommandContextHelper arg is an BaseEvent so you can pass it directly to FJsMacros#runScript(java.lang.String,xyz.wagyourtail.jsmacros.core.event.BaseEvent) .

make sure your callback returns a boolean success = true.

		Args:
			callback: 
		"""
		pass

	@overload
	def suggestMatching(self, suggestions: List[str]) -> "CommandBuilder":
		"""
		Since: 1.6.5 

		Args:
			suggestions: 
		"""
		pass

	@overload
	def suggestIdentifier(self, suggestions: List[str]) -> "CommandBuilder":
		"""
		Since: 1.6.5 

		Args:
			suggestions: 
		"""
		pass

	@overload
	def suggest(self, callback: MethodWrapper) -> "CommandBuilder":
		"""
		Since: 1.6.5 

		Args:
			callback: 
		"""
		pass

	@overload
	def or_(self) -> "CommandBuilder":
		pass

	@overload
	def otherwise(self) -> "CommandBuilder":
		"""name overload for CommandBuilder#or() to work around language keyword restrictions\n
		Since: 1.5.2 
		"""
		pass

	@overload
	def or_(self, argumentLevel: int) -> "CommandBuilder":
		pass

	@overload
	def otherwise(self, argLevel: int) -> "CommandBuilder":
		"""name overload for CommandBuilder#or(int) to work around language keyword restrictions\n
		Since: 1.5.2 

		Args:
			argLevel: 
		"""
		pass

	@overload
	def register(self) -> None:
		pass

	@overload
	def unregister(self) -> None:
		"""
		Since: 1.6.5
removes this command 
		"""
		pass

	pass


