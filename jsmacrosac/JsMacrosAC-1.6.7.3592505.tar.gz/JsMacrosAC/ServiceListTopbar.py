from typing import overload
from typing import TypeVar
from .MultiElementContainer import MultiElementContainer
from .ServiceScreen import ServiceScreen

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class ServiceListTopbar(MultiElementContainer):

	@overload
	def __init__(self, parent: ServiceScreen, x: int, y: int, width: int, height: int, textRenderer: TextRenderer) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


