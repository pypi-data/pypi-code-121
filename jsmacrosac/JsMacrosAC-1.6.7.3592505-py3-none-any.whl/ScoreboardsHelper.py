from typing import overload
from typing import List
from typing import TypeVar
from .BaseHelper import BaseHelper
from .ScoreboardObjectiveHelper import ScoreboardObjectiveHelper
from .PlayerEntityHelper import PlayerEntityHelper
from .TeamHelper import TeamHelper

Scoreboard = TypeVar["net.minecraft.scoreboard.Scoreboard"]

class ScoreboardsHelper(BaseHelper):
	"""
	Since: 1.2.9 
	"""

	@overload
	def __init__(self, board: Scoreboard) -> None:
		pass

	@overload
	def getObjectiveForTeamColorIndex(self, index: int) -> ScoreboardObjectiveHelper:
		"""
		Since: 1.2.9 

		Args:
			index: 
		"""
		pass

	@overload
	def getObjectiveSlot(self, slot: int) -> ScoreboardObjectiveHelper:
		"""'0' is tab list, '1' or '3 + getPlayerTeamColorIndex()' is sidebar, '2' should be below name.
therefore max slot number is 18.\n
		Since: 1.2.9 

		Args:
			slot: 
		"""
		pass

	@overload
	def getPlayerTeamColorIndex(self, entity: PlayerEntityHelper) -> int:
		"""
		Since: 1.2.9 

		Args:
			entity: 
		"""
		pass

	@overload
	def getPlayerTeamColorIndex(self) -> int:
		"""
		Since: 1.6.5 

		Returns:
			team index for client player 
		"""
		pass

	@overload
	def getTeams(self) -> List[TeamHelper]:
		"""
		Since: 1.3.0 
		"""
		pass

	@overload
	def getPlayerTeam(self, p: PlayerEntityHelper) -> TeamHelper:
		"""
		Since: 1.3.0 

		Args:
			p: 
		"""
		pass

	@overload
	def getPlayerTeam(self) -> TeamHelper:
		"""
		Since: 1.6.5 

		Returns:
			team for client player 
		"""
		pass

	@overload
	def getCurrentScoreboard(self) -> ScoreboardObjectiveHelper:
		"""
		Since: 1.2.9 

		Returns:
			the ScoreboardObjectiveHelper for the currently displayed sidebar scoreboard. 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


