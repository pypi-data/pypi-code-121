from typing import overload
from typing import TypeVar
from typing import Mapping
from .BaseHelper import BaseHelper
from .BlockHelper import BlockHelper
from .BlockPosHelper import BlockPosHelper

BlockState = TypeVar["net.minecraft.block.BlockState"]

class BlockStateHelper(BaseHelper):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, base: BlockState) -> None:
		pass

	@overload
	def toMap(self) -> Mapping[str, str]:
		"""

		Returns:
			a map of the state properties with its identifier and value. 
		"""
		pass

	@overload
	def getBlock(self) -> BlockHelper:
		"""

		Returns:
			the block the state belongs to. 
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
	def getLuminance(self) -> int:
		"""

		Returns:
			the luminance. 
		"""
		pass

	@overload
	def emitsRedstonePower(self) -> bool:
		"""

		Returns:
			'true' if the state emits redstone power. 
		"""
		pass

	@overload
	def exceedsCube(self) -> bool:
		"""

		Returns:
			'true' if the shape of the state is a cube. 
		"""
		pass

	@overload
	def isAir(self) -> bool:
		"""

		Returns:
			'true' if the state is air. 
		"""
		pass

	@overload
	def isOpaque(self) -> bool:
		"""

		Returns:
			'true' if the state is opaque. 
		"""
		pass

	@overload
	def isToolRequired(self) -> bool:
		"""

		Returns:
			'true' if a tool is required to mine the block. 
		"""
		pass

	@overload
	def hasBlockEntity(self) -> bool:
		"""

		Returns:
			'true' if the state has a block entity. 
		"""
		pass

	@overload
	def hasRandomTicks(self) -> bool:
		"""

		Returns:
			'true' if the state can be random ticked. 
		"""
		pass

	@overload
	def hasComparatorOutput(self) -> bool:
		"""

		Returns:
			'true' if the state has a comparator output. 
		"""
		pass

	@overload
	def getPistonBehaviour(self) -> str:
		"""

		Returns:
			the piston behaviour of the state. 
		"""
		pass

	@overload
	def blocksLight(self) -> bool:
		"""

		Returns:
			'true' if the state blocks light. 
		"""
		pass

	@overload
	def blocksMovement(self) -> bool:
		"""

		Returns:
			'true' if the state blocks the movement of entities. 
		"""
		pass

	@overload
	def isBurnable(self) -> bool:
		"""

		Returns:
			'true' if the state is burnable. 
		"""
		pass

	@overload
	def isLiquid(self) -> bool:
		"""

		Returns:
			'true' if the state is a liquid. 
		"""
		pass

	@overload
	def isSolid(self) -> bool:
		"""

		Returns:
			'true' if the state is solid. 
		"""
		pass

	@overload
	def isReplaceable(self) -> bool:
		"""This will return true for blocks like air and grass, that can be replaced
without breaking them first.

		Returns:
			'true' if the state can be replaced. 
		"""
		pass

	@overload
	def allowsSpawning(self, pos: BlockPosHelper, entity: str) -> bool:
		"""

		Args:
			pos: 
			entity: 

		Returns:
			'true' if the entity can spawn on this block state at the given position in the current world. 
		"""
		pass

	@overload
	def shouldSuffocate(self, pos: BlockPosHelper) -> bool:
		"""

		Args:
			pos: 

		Returns:
			'true' if an entity can suffocate in this block state at the given position in the current world. 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


