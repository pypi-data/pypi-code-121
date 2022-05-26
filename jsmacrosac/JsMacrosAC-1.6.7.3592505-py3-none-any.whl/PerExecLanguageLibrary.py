from typing import overload
from typing import TypeVar
from typing import Generic
from .BaseLibrary import BaseLibrary
from .BaseScriptContext import BaseScriptContext

T = TypeVar("T")

class PerExecLanguageLibrary(Generic[T], BaseLibrary):

	@overload
	def __init__(self, context: BaseScriptContext, language: Class) -> None:
		pass

	pass


