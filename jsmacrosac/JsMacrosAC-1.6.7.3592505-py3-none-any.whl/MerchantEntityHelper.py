from typing import overload
from typing import List
from typing import TypeVar
from typing import Generic
from .LivingEntityHelper import LivingEntityHelper
from .TradeOfferHelper import TradeOfferHelper

T = TypeVar("T")

class MerchantEntityHelper(Generic[T], LivingEntityHelper):

	@overload
	def __init__(self, e: T) -> None:
		pass

	@overload
	def getTrades(self) -> List[TradeOfferHelper]:
		"""these might not work... depends on the data the server sends, maybe just singleplayer.
		"""
		pass

	@overload
	def refreshTrades(self) -> List[TradeOfferHelper]:
		pass

	@overload
	def getExperience(self) -> int:
		"""
		"""
		pass

	@overload
	def hasCustomer(self) -> bool:
		"""
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


