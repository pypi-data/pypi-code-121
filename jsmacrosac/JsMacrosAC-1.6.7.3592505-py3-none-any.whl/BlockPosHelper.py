from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper

BlockPos = TypeVar["net.minecraft.util.math.BlockPos"]

class BlockPosHelper(BaseHelper):
	"""
	Since: 1.2.6 
	"""

	@overload
	def __init__(self, b: BlockPos) -> None:
		pass

	@overload
	def __init__(self, x: int, y: int, z: int) -> None:
		pass

	@overload
	def getX(self) -> int:
		"""
		Since: 1.2.6 

		Returns:
			the 'x' value of the block. 
		"""
		pass

	@overload
	def getY(self) -> int:
		"""
		Since: 1.2.6 

		Returns:
			the 'y' value of the block. 
		"""
		pass

	@overload
	def getZ(self) -> int:
		"""
		Since: 1.2.6 

		Returns:
			the 'z' value of the block. 
		"""
		pass

	@overload
	def up(self) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Returns:
			the block above. 
		"""
		pass

	@overload
	def up(self, distance: int) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Args:
			distance: 

		Returns:
			the block n-th block above. 
		"""
		pass

	@overload
	def down(self) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Returns:
			the block below. 
		"""
		pass

	@overload
	def down(self, distance: int) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Args:
			distance: 

		Returns:
			the block n-th block below. 
		"""
		pass

	@overload
	def north(self) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Returns:
			the block to the north. 
		"""
		pass

	@overload
	def north(self, distance: int) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Args:
			distance: 

		Returns:
			the n-th block to the north. 
		"""
		pass

	@overload
	def south(self) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Returns:
			the block to the south. 
		"""
		pass

	@overload
	def south(self, distance: int) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Args:
			distance: 

		Returns:
			the n-th block to the south. 
		"""
		pass

	@overload
	def east(self) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Returns:
			the block to the east. 
		"""
		pass

	@overload
	def east(self, distance: int) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Args:
			distance: 

		Returns:
			the n-th block to the east. 
		"""
		pass

	@overload
	def west(self) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Returns:
			the block to the west. 
		"""
		pass

	@overload
	def west(self, distance: int) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Args:
			distance: 

		Returns:
			the n-th block to the west. 
		"""
		pass

	@overload
	def offset(self, direction: str) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Args:
			direction: 

		Returns:
			the block offset by the given direction. 
		"""
		pass

	@overload
	def offset(self, direction: str, distance: int) -> "BlockPosHelper":
		"""
		Since: 1.6.5 

		Args:
			distance: 
			direction: 

		Returns:
			the n-th block offset by the given direction. 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


