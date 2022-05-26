from typing import overload
from typing import TypeVar
from .RenderCommon_RenderElement import RenderCommon_RenderElement

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]

class RenderCommon_Image(RenderCommon_RenderElement):
	"""
	Since: 1.2.3 
	"""
	rotation: float
	x: int
	y: int
	width: int
	height: int
	imageX: int
	imageY: int
	regionWidth: int
	regionHeight: int
	textureWidth: int
	textureHeight: int
	color: int
	zIndex: int

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, zIndex: int, color: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int, rotation: float) -> None:
		pass

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, zIndex: int, alpha: int, color: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int, rotation: float) -> None:
		pass

	@overload
	def setColor(self, color: int) -> "RenderCommon_Image":
		"""
		Since: 1.6.5 

		Args:
			color: 
		"""
		pass

	@overload
	def setColor(self, color: int, alpha: int) -> "RenderCommon_Image":
		"""
		Since: 1.6.5 

		Args:
			color: 
			alpha: 
		"""
		pass

	@overload
	def setPos(self, x: int, y: int, width: int, height: int) -> None:
		"""
		Since: 1.2.3 

		Args:
			x: 
			width: 
			y: 
			height: 
		"""
		pass

	@overload
	def setRotation(self, rotation: float) -> "RenderCommon_Image":
		"""
		Since: 1.2.6 

		Args:
			rotation: 
		"""
		pass

	@overload
	def setImage(self, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int) -> None:
		"""
		Since: 1.2.3 

		Args:
			imageY: 
			textureWidth: 
			imageX: 
			regionHeight: 
			id: 
			regionWidth: 
			textureHeight: 
		"""
		pass

	@overload
	def getImage(self) -> str:
		"""
		Since: 1.2.3 
		"""
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def getZIndex(self) -> int:
		pass

	pass


