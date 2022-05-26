from typing import overload
from typing import TypeVar
from typing import Mapping
from .IBossBarHud import IBossBarHud

ClientBossBar = TypeVar["net.minecraft.client.gui.hud.ClientBossBar"]
UUID = TypeVar["java.util.UUID"]

class MixinBossBarHud(IBossBarHud):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_GetBossBars(self) -> Mapping[UUID, ClientBossBar]:
		pass

	pass


