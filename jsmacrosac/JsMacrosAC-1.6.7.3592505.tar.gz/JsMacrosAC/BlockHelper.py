from typing import overload
from typing import List
from typing import TypeVar
from .BaseHelper import BaseHelper
from .BlockStateHelper import BlockStateHelper
from .ItemStackHelper import ItemStackHelper

Block = TypeVar["net.minecraft.block.Block"]

class BlockHelper(BaseHelper):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, base: Block) -> None:
		pass

	@overload
	def getDefaultState(self) -> BlockStateHelper:
		"""

		Returns:
			the default state of the block. 
		"""
		pass

	@overload
	def getDefaultItemStack(self) -> ItemStackHelper:
		"""

		Returns:
			the default item stack of the block. 
		"""
		pass

	@overload
	def canMobSpawnInside(self) -> bool:
		pass

	@overload
	def hasDynamicBounds(self) -> bool:
		"""

		Returns:
			'true' if the block has dynamic bounds. 
		"""
		pass

	@overload
	def getBlastResistance(self) -> float:
		"""

		Returns:
			the blast resistance. 
		"""
		pass

	@overload
	def getJumpVelocityMultiplier(self) -> float:
		"""

		Returns:
			the jump velocity multiplier. 
		"""
		pass

	@overload
	def getSlipperiness(self) -> float:
		"""

		Returns:
			the slipperiness. 
		"""
		pass

	@overload
	def getHardness(self) -> float:
		"""

		Returns:
			the hardness. 
		"""
		pass

	@overload
	def getVelocityMultiplier(self) -> float:
		"""

		Returns:
			the velocity multiplier. 
		"""
		pass

	@overload
	def getTags(self) -> List[str]:
		"""

		Returns:
			all tags of the block as an ArrayList . 
		"""
		pass

	@overload
	def getStates(self) -> List[BlockStateHelper]:
		"""

		Returns:
			all possible block states of the block. 
		"""
		pass

	@overload
	def getId(self) -> str:
		"""

		Returns:
			the identifier of the block. 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


