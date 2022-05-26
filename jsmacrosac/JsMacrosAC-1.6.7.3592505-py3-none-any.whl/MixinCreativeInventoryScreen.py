from typing import overload
from typing import TypeVar

SlotActionType = TypeVar["net.minecraft.screen.slot.SlotActionType"]
CallbackInfo = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfo"]
Slot = TypeVar["net.minecraft.screen.slot.Slot"]

class MixinCreativeInventoryScreen:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def beforeMouseClick(self, slot: Slot, slotId: int, button: int, actionType: SlotActionType, ci: CallbackInfo) -> None:
		pass

	pass


