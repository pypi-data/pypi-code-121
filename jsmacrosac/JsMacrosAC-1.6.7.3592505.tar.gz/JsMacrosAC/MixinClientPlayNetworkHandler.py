from typing import overload
from typing import TypeVar

WorldTimeUpdateS2CPacket = TypeVar["net.minecraft.network.packet.s2c.play.WorldTimeUpdateS2CPacket"]
CallbackInfo = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfo"]
GameJoinS2CPacket = TypeVar["net.minecraft.network.packet.s2c.play.GameJoinS2CPacket"]

class MixinClientPlayNetworkHandler:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def onServerTime(self, packet: WorldTimeUpdateS2CPacket, info: CallbackInfo) -> None:
		pass

	@overload
	def onGameJoin(self, packet: GameJoinS2CPacket, info: CallbackInfo) -> None:
		pass

	pass


