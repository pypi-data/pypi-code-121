from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .ClientPlayerEntityHelper import ClientPlayerEntityHelper

ClientPlayerEntity = TypeVar["net.minecraft.client.network.ClientPlayerEntity"]

class EventJoinServer(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	player: ClientPlayerEntityHelper
	address: str

	@overload
	def __init__(self, player: ClientPlayerEntity, address: str) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


