from typing import overload
from typing import TypeVar
from .BaseEvent import BaseEvent
from .BlockDataHelper import BlockDataHelper

BlockState = TypeVar["net.minecraft.block.BlockState"]
BlockPos = TypeVar["net.minecraft.util.math.BlockPos"]
BlockEntity = TypeVar["net.minecraft.block.entity.BlockEntity"]

class EventBlockUpdate(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	block: BlockDataHelper
	updateType: str

	@overload
	def __init__(self, block: BlockState, blockEntity: BlockEntity, blockPos: BlockPos, updateType: str) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


