from typing import overload
from typing import TypeVar

CallbackInfo = TypeVar["org.spongepowered.asm.mixin.injection.callback.CallbackInfo"]
Screen = TypeVar["net.minecraft.client.gui.screen.Screen"]
ClientWorld = TypeVar["net.minecraft.client.world.ClientWorld"]

class MixinMinecraftClient:
	currentScreen: Screen
	interactionManager: ClientPlayerInteractionManager

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def setScreen(self, screen: Screen) -> None:
		pass

	@overload
	def onJoinWorld(self, world: ClientWorld, info: CallbackInfo) -> None:
		pass

	@overload
	def onOpenScreen(self, screen: Screen, info: CallbackInfo) -> None:
		pass

	@overload
	def afterOpenScreen(self, screen: Screen, info: CallbackInfo) -> None:
		pass

	@overload
	def onDisconnect(self, s: Screen, info: CallbackInfo) -> None:
		pass

	pass


