from typing import overload
from typing import TypeVar
from .BaseScreen import BaseScreen
from .BaseScriptContext import BaseScriptContext
from .RunningContextContainer import RunningContextContainer

Screen = TypeVar["net.minecraft.client.gui.screen.Screen"]
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]

class CancelScreen(BaseScreen):

	@overload
	def __init__(self, parent: Screen) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def addContainer(self, t: BaseScriptContext) -> None:
		pass

	@overload
	def removeContainer(self, t: RunningContextContainer) -> None:
		pass

	@overload
	def updatePos(self) -> None:
		pass

	@overload
	def mouseScrolled(self, mouseX: float, mouseY: float, amount: float) -> bool:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def removed(self) -> None:
		pass

	@overload
	def close(self) -> None:
		pass

	pass


