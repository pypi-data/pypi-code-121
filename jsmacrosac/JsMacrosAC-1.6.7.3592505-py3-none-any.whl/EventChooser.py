from typing import overload
from typing import TypeVar
from .OverlayContainer import OverlayContainer
from .IOverlayParent import IOverlayParent

Consumer = TypeVar["java.util.function.Consumer_java.lang.String_"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class EventChooser(OverlayContainer):

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, selected: str, parent: IOverlayParent, setEvent: Consumer) -> None:
		pass

	@overload
	def selectEvent(self, event: str) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def addEvent(self, eventName: str) -> None:
		pass

	@overload
	def updateEventPos(self) -> None:
		pass

	@overload
	def onScrollbar(self, page: float) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


