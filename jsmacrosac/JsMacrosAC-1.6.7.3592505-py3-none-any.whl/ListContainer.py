from typing import overload
from typing import List
from typing import TypeVar
from .MultiElementContainer import MultiElementContainer
from .IOverlayParent import IOverlayParent

Consumer = TypeVar["java.util.function.Consumer_java.lang.Integer_"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Text = TypeVar["net.minecraft.text.Text"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class ListContainer(MultiElementContainer):
	onSelect: Consumer

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, list: List[Text], parent: IOverlayParent, onSelect: Consumer) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def addItem(self, name: Text) -> None:
		pass

	@overload
	def setSelected(self, index: int) -> None:
		pass

	@overload
	def onScrollbar(self, page: float) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


