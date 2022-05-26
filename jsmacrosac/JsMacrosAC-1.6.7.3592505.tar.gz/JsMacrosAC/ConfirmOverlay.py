from typing import overload
from typing import TypeVar
from .OverlayContainer import OverlayContainer
from .IOverlayParent import IOverlayParent

Consumer = TypeVar["java.util.function.Consumer_xyz.wagyourtail.wagyourgui.overlays.ConfirmOverlay_"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Text = TypeVar["net.minecraft.text.Text"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class ConfirmOverlay(OverlayContainer):
	hcenter: bool

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, message: Text, parent: IOverlayParent, accept: Consumer) -> None:
		pass

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, hcenter: bool, textRenderer: TextRenderer, message: Text, parent: IOverlayParent, accept: Consumer) -> None:
		pass

	@overload
	def setMessage(self, message: Text) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


