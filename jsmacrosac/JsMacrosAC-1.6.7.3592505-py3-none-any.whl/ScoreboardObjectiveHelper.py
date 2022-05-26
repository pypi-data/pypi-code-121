from typing import overload
from typing import TypeVar
from typing import Mapping
from .BaseHelper import BaseHelper
from .TextHelper import TextHelper

ScoreboardObjective = TypeVar["net.minecraft.scoreboard.ScoreboardObjective"]

class ScoreboardObjectiveHelper(BaseHelper):
	"""
	Since: 1.2.9 
	"""

	@overload
	def __init__(self, o: ScoreboardObjective) -> None:
		pass

	@overload
	def getPlayerScores(self) -> Mapping[str, int]:
		"""

		Returns:
			player name to score map 
		"""
		pass

	@overload
	def getName(self) -> str:
		"""
		Since: 1.2.9 

		Returns:
			name of scoreboard 
		"""
		pass

	@overload
	def getDisplayName(self) -> TextHelper:
		"""
		Since: 1.2.9 

		Returns:
			name of scoreboard 
		"""
		pass

	pass


