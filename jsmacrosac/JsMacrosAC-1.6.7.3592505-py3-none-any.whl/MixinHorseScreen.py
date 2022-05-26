from typing import overload
from typing import TypeVar
from .IHorseScreen import IHorseScreen

Entity = TypeVar["net.minecraft.entity.Entity"]

class MixinHorseScreen(IHorseScreen):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_getEntity(self) -> Entity:
		pass

	pass


