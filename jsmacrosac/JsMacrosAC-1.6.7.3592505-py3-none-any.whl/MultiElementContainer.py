from typing import overload
from typing import List
from typing import TypeVar
from typing import Generic
from .IContainerParent import IContainerParent
from .OverlayContainer import OverlayContainer
from .IOverlayParent import IOverlayParent

T = TypeVar("T")
DrawableHelper = TypeVar["net.minecraft.client.gui.DrawableHelper"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Element = TypeVar["net.minecraft.client.gui.Element"]
ClickableWidget = TypeVar["net.minecraft.client.gui.widget.ClickableWidget"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class MultiElementContainer(IContainerParent, Generic[T], DrawableHelper):
	parent: T
	x: int
	y: int
	width: int
	height: int

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, parent: T) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def getVisible(self) -> bool:
		pass

	@overload
	def setVisible(self, visible: bool) -> None:
		pass

	@overload
	def addDrawableChild(self, drawableElement: T) -> T:
		pass

	@overload
	def getButtons(self) -> List[ClickableWidget]:
		pass

	@overload
	def setPos(self, x: int, y: int, width: int, height: int) -> None:
		pass

	@overload
	def openOverlay(self, overlay: OverlayContainer) -> None:
		pass

	@overload
	def openOverlay(self, overlay: OverlayContainer, disableButtons: bool) -> None:
		pass

	@overload
	def remove(self, button: Element) -> None:
		pass

	@overload
	def getFirstOverlayParent(self) -> IOverlayParent:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


