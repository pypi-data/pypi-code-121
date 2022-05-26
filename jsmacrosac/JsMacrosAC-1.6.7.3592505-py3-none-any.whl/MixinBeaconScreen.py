from typing import overload
from typing import TypeVar
from .IBeaconScreen import IBeaconScreen

StatusEffect = TypeVar["net.minecraft.entity.effect.StatusEffect"]

class MixinBeaconScreen(IBeaconScreen):

	@overload
	def __init__(self) -> None:
		pass

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


