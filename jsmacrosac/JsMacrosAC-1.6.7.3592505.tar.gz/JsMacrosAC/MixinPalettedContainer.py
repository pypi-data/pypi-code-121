from typing import overload
from typing import TypeVar
from typing import Generic
from .IPalettedContainer import IPalettedContainer
from .IPalettedContainerData import IPalettedContainerData

T = TypeVar("T")
PalettedContainer_PaletteProvider = TypeVar["net.minecraft.world.chunk.PalettedContainer.PaletteProvider"]

class MixinPalettedContainer(IPalettedContainer, Generic[T]):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_getData(self) -> IPalettedContainerData:
		pass

	@overload
	def jsmacros_getPaletteProvider(self) -> PalettedContainer_PaletteProvider:
		pass

	pass


