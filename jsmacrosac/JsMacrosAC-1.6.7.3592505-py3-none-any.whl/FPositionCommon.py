from typing import overload
from .BaseLibrary import BaseLibrary
from .PositionCommon_Vec3D import PositionCommon_Vec3D
from .PositionCommon_Vec2D import PositionCommon_Vec2D
from .PositionCommon_Pos3D import PositionCommon_Pos3D
from .PositionCommon_Pos2D import PositionCommon_Pos2D


class FPositionCommon(BaseLibrary):
	"""position helper classes\n
	Since: 1.6.3 
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def createVec(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> PositionCommon_Vec3D:
		"""create a new vector object\n
		Since: 1.6.3 

		Args:
			z1: 
			y1: 
			z2: 
			x1: 
			y2: 
			x2: 
		"""
		pass

	@overload
	def createVec(self, x1: float, y1: float, x2: float, y2: float) -> PositionCommon_Vec2D:
		"""
		Since: 1.6.3 

		Args:
			y1: 
			x1: 
			y2: 
			x2: 
		"""
		pass

	@overload
	def createPos(self, x: float, y: float, z: float) -> PositionCommon_Pos3D:
		"""
		Since: 1.6.3 

		Args:
			x: 
			y: 
			z: 
		"""
		pass

	@overload
	def createPos(self, x: float, y: float) -> PositionCommon_Pos2D:
		"""
		Since: 1.6.3 

		Args:
			x: 
			y: 
		"""
		pass

	pass


