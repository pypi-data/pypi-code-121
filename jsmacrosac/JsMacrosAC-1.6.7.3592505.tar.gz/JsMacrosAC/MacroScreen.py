from typing import overload
from typing import TypeVar
from .BaseScreen import BaseScreen
from .ScriptTrigger import ScriptTrigger
from .MultiElementContainer import MultiElementContainer
from .MacroContainer import MacroContainer

Screen = TypeVar["net.minecraft.client.gui.screen.Screen"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
File = TypeVar["java.io.File"]

class MacroScreen(BaseScreen):

	@overload
	def __init__(self, parent: Screen) -> None:
		pass

	@overload
	def mouseScrolled(self, mouseX: float, mouseY: float, amount: float) -> bool:
		pass

	@overload
	def addMacro(self, macro: ScriptTrigger) -> None:
		pass

	@overload
	def setFile(self, macro: MultiElementContainer) -> None:
		pass

	@overload
	def setEvent(self, macro: MacroContainer) -> None:
		pass

	@overload
	def runFile(self) -> None:
		pass

	@overload
	def confirmRemoveMacro(self, macro: MultiElementContainer) -> None:
		pass

	@overload
	def removeMacro(self, macro: MultiElementContainer) -> None:
		pass

	@overload
	def setMacroPos(self) -> None:
		pass

	@overload
	def editFile(self, file: File) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def updateSettings(self) -> None:
		pass

	@overload
	def close(self) -> None:
		pass

	pass


