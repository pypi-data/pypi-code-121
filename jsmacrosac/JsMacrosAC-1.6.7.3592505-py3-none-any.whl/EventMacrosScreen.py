from typing import overload
from typing import TypeVar
from .MacroScreen import MacroScreen

Screen = TypeVar["net.minecraft.client.gui.screen.Screen"]

class EventMacrosScreen(MacroScreen):

	@overload
	def __init__(self, parent: Screen) -> None:
		pass

	pass


