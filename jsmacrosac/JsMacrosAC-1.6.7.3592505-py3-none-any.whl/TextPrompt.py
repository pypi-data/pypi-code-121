from typing import overload
from typing import TypeVar
from .OverlayContainer import OverlayContainer
from .TextInput import TextInput
from .IOverlayParent import IOverlayParent

Consumer = TypeVar["java.util.function.Consumer_java.lang.String_"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Text = TypeVar["net.minecraft.text.Text"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class TextPrompt(OverlayContainer):
	ti: TextInput

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, message: Text, defaultText: str, parent: IOverlayParent, accept: Consumer) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


