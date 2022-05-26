from typing import overload
from typing import TypeVar
from .BaseScriptContext import BaseScriptContext
from .BaseEvent import BaseEvent

File = TypeVar["java.io.File"]

class JSScriptContext(BaseScriptContext):

	@overload
	def __init__(self, event: BaseEvent, file: File) -> None:
		pass

	@overload
	def closeContext(self) -> None:
		pass

	pass


