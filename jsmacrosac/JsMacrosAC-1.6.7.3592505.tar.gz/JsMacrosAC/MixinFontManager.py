from typing import overload
from typing import TypeVar
from typing import Set
from .IFontManager import IFontManager

Identifier = TypeVar["net.minecraft.util.Identifier"]

class MixinFontManager(IFontManager):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_getFontList(self) -> Set[Identifier]:
		pass

	pass


