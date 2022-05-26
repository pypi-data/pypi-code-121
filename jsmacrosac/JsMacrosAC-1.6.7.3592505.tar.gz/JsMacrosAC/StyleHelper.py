from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper

Runnable = TypeVar["java.lang.Runnable"]
Style = TypeVar["net.minecraft.text.Style"]

class StyleHelper(BaseHelper):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, base: Style) -> None:
		pass

	@overload
	def hasColor(self) -> bool:
		pass

	@overload
	def getColor(self) -> int:
		pass

	@overload
	def hasCustomColor(self) -> bool:
		pass

	@overload
	def getCustomColor(self) -> int:
		pass

	@overload
	def bold(self) -> bool:
		pass

	@overload
	def italic(self) -> bool:
		pass

	@overload
	def underlined(self) -> bool:
		pass

	@overload
	def strikethrough(self) -> bool:
		pass

	@overload
	def obfuscated(self) -> bool:
		pass

	@overload
	def getClickAction(self) -> str:
		pass

	@overload
	def getClickValue(self) -> str:
		pass

	@overload
	def getCustomClickValue(self) -> Runnable:
		pass

	@overload
	def getHoverAction(self) -> str:
		pass

	@overload
	def getHoverValue(self) -> object:
		pass

	@overload
	def getInsertion(self) -> str:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


