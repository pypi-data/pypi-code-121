from typing import overload
from typing import TypeVar
from .PositionCommon_Vec2D import PositionCommon_Vec2D
from .PositionCommon_Pos3D import PositionCommon_Pos3D

Vec3f = TypeVar["net.minecraft.util.math.Vec3f"]

class PositionCommon_Vec3D(PositionCommon_Vec2D):
	"""
	Since: 1.2.6 [citation needed] 
	"""
	z1: float
	z2: float

	@overload
	def __init__(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> None:
		pass

	@overload
	def __init__(self, start: PositionCommon_Pos3D, end: PositionCommon_Pos3D) -> None:
		pass

	@overload
	def getZ1(self) -> float:
		pass

	@overload
	def getZ2(self) -> float:
		pass

	@overload
	def getDeltaZ(self) -> float:
		pass

	@overload
	def getStart(self) -> PositionCommon_Pos3D:
		pass

	@overload
	def getEnd(self) -> PositionCommon_Pos3D:
		pass

	@overload
	def getMagnitude(self) -> float:
		pass

	@overload
	def getMagnitudeSq(self) -> float:
		pass

	@overload
	def add(self, vec: "PositionCommon_Vec3D") -> "PositionCommon_Vec3D":
		pass

	@overload
	def addStart(self, pos: PositionCommon_Pos3D) -> "PositionCommon_Vec3D":
		"""
		Since: 1.6.4 

		Args:
			pos: 
		"""
		pass

	@overload
	def addEnd(self, pos: PositionCommon_Pos3D) -> "PositionCommon_Vec3D":
		"""
		Since: 1.6.4 

		Args:
			pos: 
		"""
		pass

	@overload
	def addStart(self, x: float, y: float, z: float) -> "PositionCommon_Vec3D":
		"""
		Since: 1.6.4 

		Args:
			x: 
			y: 
			z: 
		"""
		pass

	@overload
	def addEnd(self, x: float, y: float, z: float) -> "PositionCommon_Vec3D":
		"""
		Since: 1.6.4 

		Args:
			x: 
			y: 
			z: 
		"""
		pass

	@overload
	def add(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> "PositionCommon_Vec3D":
		"""
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
	def multiply(self, vec: "PositionCommon_Vec3D") -> "PositionCommon_Vec3D":
		pass

	@overload
	def multiply(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> "PositionCommon_Vec3D":
		"""
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
	def scale(self, scale: float) -> "PositionCommon_Vec3D":
		"""
		Since: 1.6.3 

		Args:
			scale: 
		"""
		pass

	@overload
	def normalize(self) -> "PositionCommon_Vec3D":
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def getPitch(self) -> float:
		pass

	@overload
	def getYaw(self) -> float:
		pass

	@overload
	def dotProduct(self, vec: "PositionCommon_Vec3D") -> float:
		pass

	@overload
	def crossProduct(self, vec: "PositionCommon_Vec3D") -> "PositionCommon_Vec3D":
		pass

	@overload
	def reverse(self) -> "PositionCommon_Vec3D":
		pass

	@overload
	def toString(self) -> str:
		pass

	@overload
	def toMojangFloatVector(self) -> Vec3f:
		"""
		Since: 1.6.5 
		"""
		pass

	pass


