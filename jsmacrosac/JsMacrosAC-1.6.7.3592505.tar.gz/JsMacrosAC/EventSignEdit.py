from typing import overload
from typing import List
from .BaseEvent import BaseEvent
from .PositionCommon_Pos3D import PositionCommon_Pos3D


class EventSignEdit(BaseEvent):
	"""
	Since: 1.2.7 
	"""
	pos: PositionCommon_Pos3D
	closeScreen: bool
	signText: List[str]

	@overload
	def __init__(self, signText: List[str], x: int, y: int, z: int) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


