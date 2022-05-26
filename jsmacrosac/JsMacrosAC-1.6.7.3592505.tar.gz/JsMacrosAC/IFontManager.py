from typing import overload
from typing import TypeVar
from typing import Set

Identifier = TypeVar["net.minecraft.util.Identifier"]

class IFontManager:

	@overload
	def jsmacros_getFontList(self) -> Set[Identifier]:
		pass

	pass


