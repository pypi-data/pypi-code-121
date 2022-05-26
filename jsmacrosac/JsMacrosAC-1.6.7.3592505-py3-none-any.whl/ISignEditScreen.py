from typing import overload


class ISignEditScreen:

	@overload
	def jsmacros_setLine(self, line: int, text: str) -> None:
		pass

	pass


