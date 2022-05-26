from typing import overload
from typing import TypeVar
from .IOverlayParent import IOverlayParent
from .OverlayContainer import OverlayContainer

T = TypeVar("T")
Screen = TypeVar["net.minecraft.client.gui.screen.Screen"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Element = TypeVar["net.minecraft.client.gui.Element"]
StringVisitable = TypeVar["net.minecraft.text.StringVisitable"]
OrderedText = TypeVar["net.minecraft.text.OrderedText"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class BaseScreen(IOverlayParent, Screen):

	@overload
	def trimmed(self, textRenderer: TextRenderer, str: StringVisitable, width: int) -> OrderedText:
		pass

	@overload
	def setParent(self, parent: Screen) -> None:
		pass

	@overload
	def reload(self) -> None:
		pass

	@overload
	def removed(self) -> None:
		pass

	@overload
	def openOverlay(self, overlay: OverlayContainer) -> None:
		pass

	@overload
	def getFirstOverlayParent(self) -> IOverlayParent:
		pass

	@overload
	def getChildOverlay(self) -> OverlayContainer:
		pass

	@overload
	def openOverlay(self, overlay: OverlayContainer, disableButtons: bool) -> None:
		pass

	@overload
	def closeOverlay(self, overlay: OverlayContainer) -> None:
		pass

	@overload
	def remove(self, btn: Element) -> None:
		pass

	@overload
	def addDrawableChild(self, drawableElement: T) -> T:
		pass

	@overload
	def setFocused(self, focused: Element) -> None:
		pass

	@overload
	def keyPressed(self, keyCode: int, scanCode: int, modifiers: int) -> bool:
		pass

	@overload
	def mouseScrolled(self, mouseX: float, mouseY: float, amount: float) -> bool:
		pass

	@overload
	def mouseClicked(self, mouseX: float, mouseY: float, button: int) -> bool:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def shouldCloseOnEsc(self) -> bool:
		pass

	@overload
	def updateSettings(self) -> None:
		pass

	@overload
	def close(self) -> None:
		pass

	@overload
	def openParent(self) -> None:
		pass

	pass


