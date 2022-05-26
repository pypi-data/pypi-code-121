from typing import overload
from typing import TypeVar

Entity = TypeVar["net.minecraft.entity.Entity"]

class IHorseScreen:

	@overload
	def jsmacros_getEntity(self) -> Entity:
		pass

	pass


