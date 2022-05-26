from typing import overload
from typing import TypeVar
from .RenderCommon_RenderElement import RenderCommon_RenderElement

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]

class RenderCommon_Rect(RenderCommon_RenderElement):
	"""
	Since: 1.0.5 
	"""
	rotation: float
	x1: int
	y1: int
	x2: int
	y2: int
	color: int
	zIndex: int

	@overload
	def __init__(self, x1: int, y1: int, x2: int, y2: int, color: int, rotation: float, zIndex: int) -> None:
		pass

	@overload
	def __init__(self, x1: int, y1: int, x2: int, y2: int, color: int, alpha: int, rotation: float, zIndex: int) -> None:
		pass

	@overload
	def setColor(self, color: int) -> "RenderCommon_Rect":
		"""
		Since: 1.0.5 

		Args:
			color: 
		"""
		pass

	@overload
	def setColor(self, color: int, alpha: int) -> "RenderCommon_Rect":
		"""
		Since: 1.1.8 

		Args:
			color: 
			alpha: 
		"""
		pass

	@overload
	def setAlpha(self, alpha: int) -> "RenderCommon_Rect":
		"""
		Since: 1.1.8 

		Args:
			alpha: 
		"""
		pass

	@overload
	def setPos(self, x1: int, y1: int, x2: int, y2: int) -> "RenderCommon_Rect":
		"""
		Since: 1.1.8 

		Args:
			y1: 
			x1: 
			y2: 
			x2: 
		"""
		pass

	@overload
	def setRotation(self, rotation: float) -> "RenderCommon_Rect":
		"""
		Since: 1.2.6 

		Args:
			rotation: 
		"""
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def getZIndex(self) -> int:
		pass

	pass


