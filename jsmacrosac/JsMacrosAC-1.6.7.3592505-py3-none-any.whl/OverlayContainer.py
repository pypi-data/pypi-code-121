from typing import overload
from typing import TypeVar
from typing import Mapping
from .IOverlayParent import IOverlayParent
from .MultiElementContainer import MultiElementContainer
from .Scrollbar import Scrollbar

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Element = TypeVar["net.minecraft.client.gui.Element"]
ClickableWidget = TypeVar["net.minecraft.client.gui.widget.ClickableWidget"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class OverlayContainer(IOverlayParent, MultiElementContainer):
	savedBtnStates: Mapping[ClickableWidget, bool]
	scroll: Scrollbar

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, parent: IOverlayParent) -> None:
		pass

	@overload
	def remove(self, btn: Element) -> None:
		pass

	@overload
	def openOverlay(self, overlay: "OverlayContainer") -> None:
		pass

	@overload
	def getFirstOverlayParent(self) -> IOverlayParent:
		pass

	@overload
	def openOverlay(self, overlay: "OverlayContainer", disableButtons: bool) -> None:
		pass

	@overload
	def getChildOverlay(self) -> "OverlayContainer":
		pass

	@overload
	def closeOverlay(self, overlay: "OverlayContainer") -> None:
		pass

	@overload
	def setFocused(self, focused: Element) -> None:
		pass

	@overload
	def onClick(self, mouseX: float, mouseY: float, button: int) -> None:
		pass

	@overload
	def keyPressed(self, keyCode: int, scanCode: int, modifiers: int) -> bool:
		"""

		Returns:
			true if should be handled by overlay 
		"""
		pass

	@overload
	def close(self) -> None:
		pass

	@overload
	def onClose(self) -> None:
		pass

	@overload
	def renderBackground(self, matrices: MatrixStack) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


