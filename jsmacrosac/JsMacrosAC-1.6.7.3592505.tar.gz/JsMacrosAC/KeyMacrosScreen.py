from typing import overload
from typing import TypeVar
from .MacroScreen import MacroScreen

Screen = TypeVar["net.minecraft.client.gui.screen.Screen"]

class KeyMacrosScreen(MacroScreen):

	@overload
	def __init__(self, parent: Screen) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def keyReleased(self, keyCode: int, scanCode: int, modifiers: int) -> bool:
		pass

	@overload
	def mouseReleased(self, mouseX: float, mouseY: float, button: int) -> bool:
		pass

	pass


