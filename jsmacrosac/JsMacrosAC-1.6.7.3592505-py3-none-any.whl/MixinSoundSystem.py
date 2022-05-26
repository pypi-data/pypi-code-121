from typing import overload
from typing import TypeVar

CallbackInfo = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfo"]
SoundInstance = TypeVar["net.minecraft.client.sound.SoundInstance"]

class MixinSoundSystem:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def onPlay(self, instance: SoundInstance, info: CallbackInfo) -> None:
		pass

	pass


