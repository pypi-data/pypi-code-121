from typing import overload
from typing import TypeVar
from .PositionCommon_Vec3D import PositionCommon_Vec3D

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]

class Draw3D_Box:
	pos: PositionCommon_Vec3D
	color: int
	fillColor: int
	fill: bool
	cull: bool

	@overload
	def __init__(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, color: int, fillColor: int, fill: bool, cull: bool) -> None:
		pass

	@overload
	def __init__(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, color: int, alpha: int, fillColor: int, fillAlpha: int, fill: bool, cull: bool) -> None:
		pass

	@overload
	def setPos(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> None:
		"""
		Since: 1.0.6 

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
	def setColor(self, color: int) -> None:
		"""
		Since: 1.0.6 

		Args:
			color: 
		"""
		pass

	@overload
	def setFillColor(self, fillColor: int) -> None:
		"""
		Since: 1.0.6 

		Args:
			fillColor: 
		"""
		pass

	@overload
	def setColor(self, color: int, alpha: int) -> None:
		"""
		Since: 1.1.8 

		Args:
			color: 
			alpha: 
		"""
		pass

	@overload
	def setAlpha(self, alpha: int) -> None:
		"""
		Since: 1.1.8 

		Args:
			alpha: 
		"""
		pass

	@overload
	def setFillColor(self, fillColor: int, alpha: int) -> None:
		"""
		Since: 1.1.8 

		Args:
			fillColor: 
			alpha: 
		"""
		pass

	@overload
	def setFillAlpha(self, alpha: int) -> None:
		"""
		Since: 1.1.8 

		Args:
			alpha: 
		"""
		pass

	@overload
	def setFill(self, fill: bool) -> None:
		"""
		Since: 1.0.6 

		Args:
			fill: 
		"""
		pass

	@overload
	def render(self, matrixStack: MatrixStack) -> None:
		pass

	pass


