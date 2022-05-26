from typing import overload
from typing import TypeVar

MinecraftClient = TypeVar["net.minecraft.client.MinecraftClient"]
MultiplayerServerListPinger = TypeVar["net.minecraft.client.network.MultiplayerServerListPinger"]
ItemStack = TypeVar["net.minecraft.item.ItemStack"]

class TickBasedEvents:
	serverListPinger: MultiplayerServerListPinger

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def areNotEqual(self, a: ItemStack, b: ItemStack) -> bool:
		pass

	@overload
	def areTagsEqualIgnoreDamage(self, a: ItemStack, b: ItemStack) -> bool:
		pass

	@overload
	def areEqualIgnoreDamage(self, a: ItemStack, b: ItemStack) -> bool:
		pass

	@overload
	def onTick(self, mc: MinecraftClient) -> None:
		pass

	pass


