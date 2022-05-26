from typing import overload
from .ISignEditScreen import ISignEditScreen


class MixinSignEditScreen(ISignEditScreen):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_setLine(self, line: int, text: str) -> None:
		pass

	pass


