from typing import overload
from typing import TypeVar
from .Button import Button

Consumer = TypeVar["java.util.function.Consumer_xyz.wagyourtail.wagyourgui.elements.Button_"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Text = TypeVar["net.minecraft.text.Text"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class AnnotatedCheckBox(Button):
	value: bool

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, color: int, borderColor: int, hilightColor: int, textColor: int, message: Text, initialValue: bool, onPress: Consumer) -> None:
		pass

	@overload
	def onPress(self) -> None:
		pass

	@overload
	def setMessage(self, message: Text) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


