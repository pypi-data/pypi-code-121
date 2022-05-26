from typing import overload
from typing import List
from typing import TypeVar
from .BaseHelper import BaseHelper
from .VillagerInventory import VillagerInventory
from .ItemStackHelper import ItemStackHelper
from .NBTElementHelper import NBTElementHelper

TradeOffer = TypeVar["net.minecraft.village.TradeOffer"]

class TradeOfferHelper(BaseHelper):

	@overload
	def __init__(self, base: TradeOffer, index: int, inv: VillagerInventory) -> None:
		pass

	@overload
	def getInput(self) -> List[ItemStackHelper]:
		"""

		Returns:
			list of input items required 
		"""
		pass

	@overload
	def getOutput(self) -> ItemStackHelper:
		"""

		Returns:
			output item that will be recieved 
		"""
		pass

	@overload
	def select(self) -> None:
		"""select trade offer on screen
		"""
		pass

	@overload
	def isAvailable(self) -> bool:
		"""
		"""
		pass

	@overload
	def getNBT(self) -> NBTElementHelper:
		"""

		Returns:
			trade offer as nbt tag 
		"""
		pass

	@overload
	def getUses(self) -> int:
		"""

		Returns:
			current number of uses 
		"""
		pass

	@overload
	def getMaxUses(self) -> int:
		"""

		Returns:
			max uses before it locks 
		"""
		pass

	@overload
	def getExperience(self) -> int:
		"""

		Returns:
			experience gained for trade 
		"""
		pass

	@overload
	def getCurrentPriceAdjustment(self) -> int:
		"""

		Returns:
			current price adjustment, negative is discount. 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


