from typing import overload
from typing import List
from typing import TypeVar
from .BaseHelper import BaseHelper
from .TextHelper import TextHelper
from .NBTElementHelper import NBTElementHelper

ServerInfo = TypeVar["net.minecraft.client.network.ServerInfo"]

class ServerInfoHelper(BaseHelper):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, base: ServerInfo) -> None:
		pass

	@overload
	def getName(self) -> str:
		pass

	@overload
	def getAddress(self) -> str:
		pass

	@overload
	def getPlayerCountLabel(self) -> TextHelper:
		pass

	@overload
	def getLabel(self) -> TextHelper:
		pass

	@overload
	def getPing(self) -> float:
		pass

	@overload
	def getProtocolVersion(self) -> int:
		pass

	@overload
	def getVersion(self) -> TextHelper:
		pass

	@overload
	def getPlayerListSummary(self) -> List[TextHelper]:
		pass

	@overload
	def resourcePackPolicy(self) -> str:
		pass

	@overload
	def getIcon(self) -> str:
		pass

	@overload
	def isOnline(self) -> bool:
		pass

	@overload
	def isLocal(self) -> bool:
		pass

	@overload
	def getNbt(self) -> NBTElementHelper:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


