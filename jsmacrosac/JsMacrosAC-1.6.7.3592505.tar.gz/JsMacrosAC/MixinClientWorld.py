from typing import overload
from typing import TypeVar

Entity = TypeVar["net.minecraft.entity.Entity"]
Entity_RemovalReason = TypeVar["net.minecraft.entity.Entity.RemovalReason"]
CallbackInfo = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfo"]

class MixinClientWorld:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def onAddEntity(self, id: int, entity: Entity, ci: CallbackInfo) -> None:
		pass

	@overload
	def onRemoveEntity(self, entityId: int, removalReason: Entity_RemovalReason, ci: CallbackInfo, entity: Entity) -> None:
		pass

	pass


