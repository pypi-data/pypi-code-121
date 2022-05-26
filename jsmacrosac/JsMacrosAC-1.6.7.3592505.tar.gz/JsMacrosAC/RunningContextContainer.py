from typing import overload
from typing import TypeVar
from .MultiElementContainer import MultiElementContainer
from .BaseScriptContext import BaseScriptContext
from .CancelScreen import CancelScreen

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class RunningContextContainer(MultiElementContainer):
	t: BaseScriptContext
	service: bool

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, parent: CancelScreen, t: BaseScriptContext) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def setPos(self, x: int, y: int, width: int, height: int) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


