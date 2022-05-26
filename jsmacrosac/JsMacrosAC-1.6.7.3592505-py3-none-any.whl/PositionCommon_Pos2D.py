from typing import overload
from .PositionCommon_Pos3D import PositionCommon_Pos3D
from .PositionCommon_Vec2D import PositionCommon_Vec2D


class PositionCommon_Pos2D:
	"""
	Since: 1.2.6 [citation needed] 
	"""
	ZERO: "PositionCommon_Pos2D"
	x: float
	y: float

	@overload
	def __init__(self, x: float, y: float) -> None:
		pass

	@overload
	def getX(self) -> float:
		pass

	@overload
	def getY(self) -> float:
		pass

	@overload
	def add(self, pos: "PositionCommon_Pos2D") -> "PositionCommon_Pos2D":
		pass

	@overload
	def add(self, x: float, y: float) -> "PositionCommon_Pos2D":
		"""
		Since: 1.6.3 

		Args:
			x: 
			y: 
		"""
		pass

	@overload
	def multiply(self, pos: "PositionCommon_Pos2D") -> "PositionCommon_Pos2D":
		pass

	@overload
	def multiply(self, x: float, y: float) -> "PositionCommon_Pos2D":
		"""
		Since: 1.6.3 

		Args:
			x: 
			y: 
		"""
		pass

	@overload
	def scale(self, scale: float) -> "PositionCommon_Pos2D":
		"""
		Since: 1.6.3 

		Args:
			scale: 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	@overload
	def to3D(self) -> PositionCommon_Pos3D:
		pass

	@overload
	def toVector(self) -> PositionCommon_Vec2D:
		pass

	@overload
	def toVector(self, start_pos: "PositionCommon_Pos2D") -> PositionCommon_Vec2D:
		"""
		Since: 1.6.4 

		Args:
			start_pos: 
		"""
		pass

	@overload
	def toVector(self, start_x: float, start_y: float) -> PositionCommon_Vec2D:
		"""
		Since: 1.6.4 

		Args:
			start_x: 
			start_y: 
		"""
		pass

	@overload
	def toReverseVector(self) -> PositionCommon_Vec2D:
		"""
		Since: 1.6.4 
		"""
		pass

	@overload
	def toReverseVector(self, end_pos: "PositionCommon_Pos2D") -> PositionCommon_Vec2D:
		"""
		Since: 1.6.4 

		Args:
			end_pos: 
		"""
		pass

	@overload
	def toReverseVector(self, end_x: float, end_y: float) -> PositionCommon_Vec2D:
		"""
		Since: 1.6.4 

		Args:
			end_x: 
			end_y: 
		"""
		pass

	pass


