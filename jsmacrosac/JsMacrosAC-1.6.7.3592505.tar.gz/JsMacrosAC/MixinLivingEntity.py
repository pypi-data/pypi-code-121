from typing import overload
from typing import TypeVar

CallbackInfo = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfo"]

class MixinLivingEntity:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def getMaxHealth(self) -> float:
		pass

	@overload
	def onSetHealth(self, health: float, ci: CallbackInfo) -> None:
		pass

	pass


