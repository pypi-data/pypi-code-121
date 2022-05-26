from typing import overload
from typing import TypeVar

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Drawable = TypeVar["net.minecraft.client.gui.Drawable"]

class RenderCommon_RenderElement(Drawable):

	@overload
	def getZIndex(self) -> int:
		pass

	@overload
	def render3D(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


