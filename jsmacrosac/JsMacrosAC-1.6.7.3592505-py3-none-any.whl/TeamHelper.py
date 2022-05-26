from typing import overload
from typing import List
from typing import TypeVar
from .BaseHelper import BaseHelper
from .TextHelper import TextHelper

Team = TypeVar["net.minecraft.scoreboard.Team"]

class TeamHelper(BaseHelper):
	"""
	Since: 1.3.0 
	"""

	@overload
	def __init__(self, t: Team) -> None:
		pass

	@overload
	def getName(self) -> str:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def getDisplayName(self) -> TextHelper:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def getPlayerList(self) -> List[str]:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def getColor(self) -> int:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def getPrefix(self) -> TextHelper:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def getSuffix(self) -> TextHelper:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def getCollisionRule(self) -> str:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def isFriendlyFire(self) -> bool:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def showFriendlyInvisibles(self) -> bool:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def nametagVisibility(self) -> str:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def deathMessageVisibility(self) -> str:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


