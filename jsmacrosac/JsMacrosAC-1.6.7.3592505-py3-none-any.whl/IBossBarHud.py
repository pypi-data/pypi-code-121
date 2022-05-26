from typing import overload
from typing import TypeVar
from typing import Mapping

ClientBossBar = TypeVar["net.minecraft.client.gui.hud.ClientBossBar"]
UUID = TypeVar["java.util.UUID"]

class IBossBarHud:

	@overload
	def jsmacros_GetBossBars(self) -> Mapping[UUID, ClientBossBar]:
		pass

	pass


