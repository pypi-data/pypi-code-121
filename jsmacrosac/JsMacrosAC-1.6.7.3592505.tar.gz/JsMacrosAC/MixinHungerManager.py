from typing import overload
from typing import TypeVar

CallbackInfo = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfo"]

class MixinHungerManager:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def onSetFoodLevel(self, foodLevel: int, info: CallbackInfo) -> None:
		pass

	pass


