from typing import overload
from typing import List
from .Inventory import Inventory
from .TradeOfferHelper import TradeOfferHelper


class VillagerInventory(Inventory):
	"""
	Since: 1.3.1 
	"""

	@overload
	def selectTrade(self, index: int) -> "VillagerInventory":
		"""select the trade by it's index\n
		Since: 1.3.1 

		Args:
			index: 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def getExperience(self) -> int:
		"""
		Since: 1.3.1 
		"""
		pass

	@overload
	def getLevelProgress(self) -> int:
		"""
		Since: 1.3.1 
		"""
		pass

	@overload
	def getMerchantRewardedExperience(self) -> int:
		"""
		Since: 1.3.1 
		"""
		pass

	@overload
	def canRefreshTrades(self) -> bool:
		"""
		Since: 1.3.1 
		"""
		pass

	@overload
	def isLeveled(self) -> bool:
		"""
		Since: 1.3.1 
		"""
		pass

	@overload
	def getTrades(self) -> List[TradeOfferHelper]:
		"""
		Since: 1.3.1 

		Returns:
			list of trade offers 
		"""
		pass

	pass


