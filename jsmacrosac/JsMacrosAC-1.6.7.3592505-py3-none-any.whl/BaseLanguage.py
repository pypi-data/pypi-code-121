from typing import overload
from typing import TypeVar
from typing import Mapping
from typing import Generic
from .Core import Core
from .ScriptTrigger import ScriptTrigger
from .BaseEvent import BaseEvent
from .EventContainer import EventContainer
from .BaseScriptContext import BaseScriptContext
from .BaseLibrary import BaseLibrary
from .BaseWrappedException import BaseWrappedException

T = TypeVar("T")
Consumer = TypeVar["java.util.function.Consumer_java.lang.Throwable_"]
Runnable = TypeVar["java.lang.Runnable"]
Throwable = TypeVar["java.lang.Throwable"]
File = TypeVar["java.io.File"]

class BaseLanguage(Generic[T]):
	"""Language class for languages to be implemented on top of.\n
	Since: 1.1.3 
	"""
	extension: str
	preThread: Runnable

	@overload
	def __init__(self, extension: str, runner: Core) -> None:
		pass

	@overload
	def trigger(self, macro: ScriptTrigger, event: BaseEvent, then: Runnable, catcher: Consumer) -> EventContainer:
		pass

	@overload
	def trigger(self, script: str, fakeFile: File, then: Runnable, catcher: Consumer) -> EventContainer:
		pass

	@overload
	def retrieveLibs(self, context: BaseScriptContext) -> Mapping[str, BaseLibrary]:
		pass

	@overload
	def retrieveOnceLibs(self) -> Mapping[str, BaseLibrary]:
		pass

	@overload
	def retrievePerExecLibs(self, context: BaseScriptContext) -> Mapping[str, BaseLibrary]:
		pass

	@overload
	def wrapException(self, ex: Throwable) -> BaseWrappedException:
		"""
		Since: 1.3.0 

		Args:
			ex: 
		"""
		pass

	@overload
	def createContext(self, event: BaseEvent, file: File) -> BaseScriptContext:
		pass

	@overload
	def extension(self) -> str:
		pass

	pass


