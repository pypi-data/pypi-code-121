from typing import overload
from typing import TypeVar

Palette = TypeVar["net.minecraft.world.chunk.Palette_T_"]
PaletteStorage = TypeVar["net.minecraft.util.collection.PaletteStorage"]

class IPalettedContainerData:

	@overload
	def jsmacros_getStorage(self) -> PaletteStorage:
		pass

	@overload
	def jsmacros_getPalette(self) -> Palette:
		pass

	pass


