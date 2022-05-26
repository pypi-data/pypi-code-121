from typing import overload
from typing import TypeVar
from .Button import Button

Consumer = TypeVar["java.util.function.Consumer_java.lang.String_"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class TextInput(Button):
	onChange: Consumer
	mask: str
	content: str
	selStartIndex: int
	selEndIndex: int

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, color: int, borderColor: int, hilightColor: int, textColor: int, message: str, onClick: Consumer, onChange: Consumer) -> None:
		pass

	@overload
	def setMessage(self, message: str) -> None:
		pass

	@overload
	def updateSelStart(self, startIndex: int) -> None:
		pass

	@overload
	def updateSelEnd(self, endIndex: int) -> None:
		pass

	@overload
	def mouseClicked(self, mouseX: float, mouseY: float, button: int) -> bool:
		pass

	@overload
	def mouseDragged(self, mouseX: float, mouseY: float, button: int, deltaX: float, deltaY: float) -> bool:
		pass

	@overload
	def swapStartEnd(self) -> None:
		pass

	@overload
	def keyPressed(self, keyCode: int, scanCode: int, modifiers: int) -> bool:
		pass

	@overload
	def charTyped(self, chr: str, keyCode: int) -> bool:
		pass

	@overload
	def clicked(self, mouseX: float, mouseY: float) -> bool:
		pass

	@overload
	def setSelected(self, sel: bool) -> None:
		pass

	pass


