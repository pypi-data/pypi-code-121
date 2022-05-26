from typing import overload
from typing import TypeVar
from .PositionCommon_Pos2D import PositionCommon_Pos2D
from .PositionCommon_Vec3D import PositionCommon_Vec3D

Vec3d = TypeVar["net.minecraft.util.math.Vec3d"]

class PositionCommon_Pos3D(PositionCommon_Pos2D):
	"""
	Since: 1.2.6 [citation needed] 
	"""
	ZERO: "PositionCommon_Pos3D"
	z: float

	@overload
	def __init__(self, vec: Vec3d) -> None:
		pass

	@overload
	def __init__(self, x: float, y: float, z: float) -> None:
		pass

	@overload
	def getZ(self) -> float:
		pass

	@overload
	def add(self, pos: "PositionCommon_Pos3D") -> "PositionCommon_Pos3D":
		pass

	@overload
	def add(self, x: float, y: float, z: float) -> "PositionCommon_Pos3D":
		"""
		Since: 1.6.3 

		Args:
			x: 
			y: 
			z: 
		"""
		pass

	@overload
	def multiply(self, pos: "PositionCommon_Pos3D") -> "PositionCommon_Pos3D":
		pass

	@overload
	def multiply(self, x: float, y: float, z: float) -> "PositionCommon_Pos3D":
		"""
		Since: 1.6.3 

		Args:
			x: 
			y: 
			z: 
		"""
		pass

	@overload
	def scale(self, scale: float) -> "PositionCommon_Pos3D":
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
	def toVector(self) -> PositionCommon_Vec3D:
		pass

	@overload
	def toVector(self, start_pos: PositionCommon_Pos2D) -> PositionCommon_Vec3D:
		"""
		Since: 1.6.4 

		Args:
			start_pos: 
		"""
		pass

	@overload
	def toVector(self, start_pos: "PositionCommon_Pos3D") -> PositionCommon_Vec3D:
		"""
		Since: 1.6.4 

		Args:
			start_pos: 
		"""
		pass

	@overload
	def toVector(self, start_x: float, start_y: float, start_z: float) -> PositionCommon_Vec3D:
		"""
		Since: 1.6.4 

		Args:
			start_x: 
			start_z: 
			start_y: 
		"""
		pass

	@overload
	def toReverseVector(self) -> PositionCommon_Vec3D:
		"""
		Since: 1.6.4 
		"""
		pass

	@overload
	def toReverseVector(self, end_pos: PositionCommon_Pos2D) -> PositionCommon_Vec3D:
		pass

	@overload
	def toReverseVector(self, end_pos: "PositionCommon_Pos3D") -> PositionCommon_Vec3D:
		"""
		Since: 1.6.4 

		Args:
			end_pos: 
		"""
		pass

	@overload
	def toReverseVector(self, end_x: float, end_y: float, end_z: float) -> PositionCommon_Vec3D:
		"""
		Since: 1.6.4 

		Args:
			end_z: 
			end_x: 
			end_y: 
		"""
		pass

	pass


