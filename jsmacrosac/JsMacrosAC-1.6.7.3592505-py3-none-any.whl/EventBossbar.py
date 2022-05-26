from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .BossBarHelper import BossBarHelper

ClientBossBar = TypeVar["net.minecraft.client.gui.hud.ClientBossBar"]
UUID = TypeVar["java.util.UUID"]

class EventBossbar(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	bossBar: BossBarHelper
	uuid: str
	type: str

	@overload
	def __init__(self, type: str, uuid: UUID, bossBar: ClientBossBar) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


