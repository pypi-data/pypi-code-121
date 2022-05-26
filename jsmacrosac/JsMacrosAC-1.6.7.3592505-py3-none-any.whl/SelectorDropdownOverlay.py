from typing import overload
from typing import List
from typing import TypeVar
from .OverlayContainer import OverlayContainer
from .IOverlayParent import IOverlayParent

Consumer = TypeVar["java.util.function.Consumer_java.lang.Integer_"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Text = TypeVar["net.minecraft.text.Text"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class SelectorDropdownOverlay(OverlayContainer):

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, choices: List[Text], textRenderer: TextRenderer, parent: IOverlayParent, onChoice: Consumer) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def onScroll(self, page: float) -> None:
		pass

	@overload
	def onClick(self, mouseX: float, mouseY: float, button: int) -> None:
		pass

	@overload
	def setSelected(self, sel: int) -> None:
		pass

	@overload
	def keyPressed(self, keyCode: int, scanCode: int, modifiers: int) -> bool:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


