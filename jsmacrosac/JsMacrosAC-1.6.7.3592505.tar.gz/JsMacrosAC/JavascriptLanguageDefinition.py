from typing import overload
from typing import TypeVar
from .BaseLanguage import BaseLanguage
from .Core import Core
from .BaseWrappedException import BaseWrappedException
from .BaseEvent import BaseEvent
from .JSScriptContext import JSScriptContext

Throwable = TypeVar["java.lang.Throwable"]
File = TypeVar["java.io.File"]

class JavascriptLanguageDefinition(BaseLanguage):

	@overload
	def __init__(self, extension: str, runner: Core) -> None:
		pass

	@overload
	def wrapException(self, ex: Throwable) -> BaseWrappedException:
		pass

	@overload
	def createContext(self, event: BaseEvent, file: File) -> JSScriptContext:
		pass

	pass


