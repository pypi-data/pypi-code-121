from typing import overload
from typing import TypeVar
from .RenderCommon_RenderElement import RenderCommon_RenderElement
from .ItemStackHelper import ItemStackHelper

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
ItemStack = TypeVar["net.minecraft.item.ItemStack"]

class RenderCommon_Item(RenderCommon_RenderElement):
	"""
	Since: 1.0.5 
	"""
	item: ItemStack
	ovText: str
	overlay: bool
	scale: float
	rotation: float
	x: int
	y: int
	zIndex: int

	@overload
	def __init__(self, x: int, y: int, zIndex: int, id: str, overlay: bool, scale: float, rotation: float) -> None:
		pass

	@overload
	def __init__(self, x: int, y: int, zIndex: int, i: ItemStackHelper, overlay: bool, scale: float, rotation: float) -> None:
		pass

	@overload
	def setPos(self, x: int, y: int) -> "RenderCommon_Item":
		"""
		Since: 1.0.5 

		Args:
			x: 
			y: 
		"""
		pass

	@overload
	def setScale(self, scale: float) -> "RenderCommon_Item":
		"""
		Since: 1.2.6 

		Args:
			scale: 
		"""
		pass

	@overload
	def setRotation(self, rotation: float) -> "RenderCommon_Item":
		"""
		Since: 1.2.6 

		Args:
			rotation: 
		"""
		pass

	@overload
	def setOverlay(self, overlay: bool) -> "RenderCommon_Item":
		"""
		Since: 1.2.0 

		Args:
			overlay: 
		"""
		pass

	@overload
	def setOverlayText(self, ovText: str) -> "RenderCommon_Item":
		"""
		Since: 1.2.0 

		Args:
			ovText: 
		"""
		pass

	@overload
	def setItem(self, i: ItemStackHelper) -> "RenderCommon_Item":
		"""
		Since: 1.0.5 [citation needed] 

		Args:
			i: 
		"""
		pass

	@overload
	def setItem(self, id: str, count: int) -> "RenderCommon_Item":
		"""
		Since: 1.0.5 [citation needed] 

		Args:
			count: 
			id: 
		"""
		pass

	@overload
	def getItem(self) -> ItemStackHelper:
		"""
		Since: 1.0.5 [citation needed] 
		"""
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def render3D(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def getZIndex(self) -> int:
		pass

	pass


