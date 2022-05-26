from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper
from .TextHelper import TextHelper

PlayerListEntry = TypeVar["net.minecraft.client.network.PlayerListEntry"]

class PlayerListEntryHelper(BaseHelper):
	"""
	Since: 1.0.2 
	"""

	@overload
	def __init__(self, p: PlayerListEntry) -> None:
		pass

	@overload
	def getUUID(self) -> str:
		"""
		Since: 1.1.9 
		"""
		pass

	@overload
	def getName(self) -> str:
		"""
		Since: 1.0.2 
		"""
		pass

	@overload
	def getPing(self) -> int:
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def getGamemode(self) -> str:
		"""
		Since: 1.6.5 

		Returns:
			null if unknown 
		"""
		pass

	@overload
	def getDisplayText(self) -> TextHelper:
		"""
		Since: 1.1.9 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


