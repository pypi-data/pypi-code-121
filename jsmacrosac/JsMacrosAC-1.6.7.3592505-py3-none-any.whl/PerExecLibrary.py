from typing import overload
from .BaseLibrary import BaseLibrary
from .BaseScriptContext import BaseScriptContext


class PerExecLibrary(BaseLibrary):

	@overload
	def __init__(self, context: BaseScriptContext) -> None:
		pass

	pass


