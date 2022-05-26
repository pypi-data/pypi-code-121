from typing import overload
from typing import TypeVar

StatusEffect = TypeVar["net.minecraft.entity.effect.StatusEffect"]

class IBeaconScreen:

	@overload
	def jsmacros_getPrimaryEffect(self) -> StatusEffect:
		pass

	@overload
	def jsmacros_setPrimaryEffect(self, effect: StatusEffect) -> None:
		pass

	@overload
	def jsmacros_getSecondaryEffect(self) -> StatusEffect:
		pass

	@overload
	def jsmacros_setSecondaryEffect(self, effect: StatusEffect) -> None:
		pass

	pass


