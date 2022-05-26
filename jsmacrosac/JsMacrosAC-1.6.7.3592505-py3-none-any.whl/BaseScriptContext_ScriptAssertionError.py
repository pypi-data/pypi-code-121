from typing import overload


class BaseScriptContext_ScriptAssertionError(AssertionError):

	@overload
	def __init__(self, message: str) -> None:
		pass

	pass


