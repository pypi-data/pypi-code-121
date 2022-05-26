from typing import overload
from typing import List
from typing import TypeVar
from typing import Mapping
from .PositionCommon_Pos3D import PositionCommon_Pos3D

Function = TypeVar["java.util.function.Function_xyz.wagyourtail.jsmacros.client.api.helpers.BlockStateHelper,java.lang.Boolean_"]
ChunkPos = TypeVar["net.minecraft.util.math.ChunkPos"]
World = TypeVar["net.minecraft.world.World"]

class WorldScanner:
	"""A class to scan the world for certain blocks. The results of the filters are cached, 
so it's a good idea to reuse an instance of this if possible. 
The scanner can either return a list of all block positions or
a list of blocks and their respective count for every block / state matching the filters criteria.\n
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, world: World, blockFilter: Function, stateFilter: Function) -> None:
		"""Creates a new World scanner with for the given world. It accepts two boolean functions, 
one for BlockHelper and the other for BlockStateHelper .

		Args:
			world: 
			blockFilter: 
			stateFilter: 
		"""
		pass

	@overload
	def getChunkRange(self, centerX: int, centerZ: int, chunkrange: int) -> List[ChunkPos]:
		"""Gets a list of all chunks in the given range around the center chunk.

		Args:
			centerZ: 
			centerX: 
			chunkrange: 
		"""
		pass

	@overload
	def scanAroundPlayer(self, range: int) -> List[PositionCommon_Pos3D]:
		"""Scans all chunks in the given range around the player and returns a list of all block positions, for blocks matching the filter.
This will scan in a square with length 2*range + 1. So range = 0 for example will only scan the chunk the player
is standing in, while range = 1 will scan in a 3x3 area.

		Args:
			range: 
		"""
		pass

	@overload
	def scanChunkRange(self, centerX: int, centerZ: int, chunkrange: int) -> List[PositionCommon_Pos3D]:
		"""Scans all chunks in the given range around the center chunk and returns a list of all block positions, for blocks matching the filter.
This will scan in a square with length 2*range + 1. So range = 0 for example will only scan the specified chunk,
while range = 1 will scan in a 3x3 area.

		Args:
			centerZ: 
			centerX: 
			chunkrange: 

		Returns:
			the list 
		"""
		pass

	@overload
	def getBlocksInChunk(self, chunkX: int, chunkZ: int, ignoreState: bool) -> Mapping[str, int]:
		"""Gets the amount of all blocks matching the criteria inside the chunk.

		Args:
			ignoreState: whether multiple states should be combined to a single block 
			chunkX: 
			chunkZ: 
		"""
		pass

	@overload
	def getBlocksInChunks(self, centerX: int, centerZ: int, chunkrange: int, ignoreState: bool) -> Mapping[str, int]:
		"""Gets the amount of all blocks matching the criteria inside square around the center chunk 
with radius chunkrange/2.

		Args:
			centerZ: 
			ignoreState: whether multiple states should be combined to a single block 
			centerX: 
			chunkrange: 
		"""
		pass

	@overload
	def getCachedAmount(self) -> int:
		"""Get the amount of cached block states. This will normally be around 200 - 400.
		"""
		pass

	pass


