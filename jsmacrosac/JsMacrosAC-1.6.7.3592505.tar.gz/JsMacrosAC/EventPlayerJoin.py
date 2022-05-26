from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .PlayerListEntryHelper import PlayerListEntryHelper

PlayerListEntry = TypeVar["net.minecraft.client.network.PlayerListEntry"]
UUID = TypeVar["java.util.UUID"]

class EventPlayerJoin(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	UUID: str
	player: PlayerListEntryHelper

	@overload
	def __init__(self, uuid: UUID, player: PlayerListEntry) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


