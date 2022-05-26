from typing import overload
from typing import TypeVar
from .IPalettedContainerData import IPalettedContainerData

PalettedContainer_PaletteProvider = TypeVar["net.minecraft.world.chunk.PalettedContainer.PaletteProvider"]

class IPalettedContainer:

	@overload
	def jsmacros_getData(self) -> IPalettedContainerData:
		pass

	@overload
	def jsmacros_getPaletteProvider(self) -> PalettedContainer_PaletteProvider:
		pass

	pass


