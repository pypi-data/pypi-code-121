from typing import overload
from typing import TypeVar
from .IMixinEntity import IMixinEntity

CallbackInfoReturnable = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable_java.lang.Boolean_"]

class MixinEntity(IMixinEntity):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_setGlowingColor(self, glowingColor: int) -> None:
		pass

	@overload
	def jsmacros_resetColor(self) -> None:
		pass

	@overload
	def getTeamColorValue(self, ci: CallbackInfoReturnable) -> None:
		pass

	@overload
	def jsmacros_setForceGlowing(self, glowing: int) -> None:
		pass

	@overload
	def isGlowing(self, cir: CallbackInfoReturnable) -> None:
		pass

	pass


