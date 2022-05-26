from typing import overload
from typing import TypeVar

NarrationMessageBuilder = TypeVar["net.minecraft.client.gui.screen.narration.NarrationMessageBuilder"]
Consumer = TypeVar["java.util.function.Consumer_xyz.wagyourtail.wagyourgui.elements.Button_"]
PressableWidget = TypeVar["net.minecraft.client.gui.widget.PressableWidget"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Text = TypeVar["net.minecraft.text.Text"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class Button(PressableWidget):
	horizCenter: bool
	onPress: Consumer
	hovering: bool
	forceHover: bool

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, color: int, borderColor: int, hilightColor: int, textColor: int, message: Text, onPress: Consumer) -> None:
		pass

	@overload
	def setPos(self, x: int, y: int, width: int, height: int) -> "Button":
		pass

	@overload
	def cantRenderAllText(self) -> bool:
		pass

	@overload
	def setMessage(self, message: Text) -> None:
		pass

	@overload
	def setColor(self, color: int) -> None:
		pass

	@overload
	def setHilightColor(self, color: int) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def onClick(self, mouseX: float, mouseY: float) -> None:
		pass

	@overload
	def onRelease(self, mouseX: float, mouseY: float) -> None:
		pass

	@overload
	def onPress(self) -> None:
		pass

	@overload
	def appendNarrations(self, builder: NarrationMessageBuilder) -> None:
		pass

	pass


