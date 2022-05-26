from typing import overload
from typing import TypeVar
from .MultiElementContainer import MultiElementContainer
from .ScriptTrigger import ScriptTrigger
from .MacroScreen import MacroScreen

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
Text = TypeVar["net.minecraft.text.Text"]
File = TypeVar["java.io.File"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class MacroContainer(MultiElementContainer):

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, macro: ScriptTrigger, parent: MacroScreen) -> None:
		pass

	@overload
	def getRawMacro(self) -> ScriptTrigger:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def setEventType(self, type: str) -> None:
		pass

	@overload
	def setFile(self, f: File) -> None:
		pass

	@overload
	def setPos(self, x: int, y: int, width: int, height: int) -> None:
		pass

	@overload
	def onKey(self, translationKey: str) -> bool:
		pass

	@overload
	def buildKeyName(self, translationKeys: str) -> Text:
		pass

	@overload
	def setKey(self, translationKeys: str) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


