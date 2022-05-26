from typing import overload
from typing import TypeVar
from typing import Generic
from .IPalettedContainerData import IPalettedContainerData

Palette = TypeVar["net.minecraft.world.chunk.Palette_T_"]
T = TypeVar("T")
PaletteStorage = TypeVar["net.minecraft.util.collection.PaletteStorage"]

class MixinPalettedContainerData(IPalettedContainerData, Generic[T]):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_getStorage(self) -> PaletteStorage:
		pass

	@overload
	def jsmacros_getPalette(self) -> Palette:
		pass

	pass


