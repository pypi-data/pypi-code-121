from typing import overload
from typing import List
from typing import TypeVar
from .ICategoryTreeParent import ICategoryTreeParent
from .OverlayContainer import OverlayContainer
from .IOverlayParent import IOverlayParent

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class SettingsOverlay(ICategoryTreeParent, OverlayContainer):

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, parent: IOverlayParent) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def clearCategory(self) -> None:
		pass

	@overload
	def selectCategory(self, category: List[str]) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def keyPressed(self, keyCode: int, scanCode: int, modifiers: int) -> bool:
		pass

	@overload
	def onClose(self) -> None:
		pass

	pass


